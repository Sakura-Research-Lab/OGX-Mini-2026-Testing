#include "Board/Config.h"
#include "OGXMini/Board/PicoW.h"
#if (OGXM_BOARD == PI_PICOW)

#include <cstdio>
#include <hardware/clocks.h>
#include <pico/multicore.h>
#include <pico/time.h>

#include "tusb.h"
#include "bsp/board_api.h"

#include "USBDevice/DeviceManager.h"
#include "UserSettings/UserSettings.h"
#include "Board/board_api.h"
#include "Bluepad32/Bluepad32.h"
#include "BLEServer/BLEServer.h"
#include "Gamepad/Gamepad.h"
#include "TaskQueue/TaskQueue.h"

Gamepad _gamepads[MAX_GAMEPADS];

void core1_task() {
    board_api::init_bluetooth();
    board_api::set_led(true);
    BLEServer::init_server(_gamepads);
    bluepad32::run_task(_gamepads);
}

void set_gp_check_timer(uint32_t task_id) {
#if !defined(CONFIG_OGXM_FIXED_DRIVER) || defined(CONFIG_OGXM_FIXED_DRIVER_ALLOW_COMBOS)
    UserSettings& user_settings = UserSettings::get_instance();
    TaskQueue::Core0::queue_delayed_task(task_id, UserSettings::GP_CHECK_DELAY_MS, true,
    [&user_settings] {
        //Check gamepad inputs for button combo to change usb device driver
        if (user_settings.check_for_driver_change(_gamepads[0])) {
            //This will store the new mode and reboot the pico
            user_settings.store_driver_type(user_settings.get_current_driver());
        }
    });
#else
    (void)task_id;  // Fixed output, combos disabled
#endif
}

void pico_w::initialize() {
    board_api::init_board();

    UserSettings& user_settings = UserSettings::get_instance();
    user_settings.initialize_flash();

    for (uint8_t i = 0; i < MAX_GAMEPADS; ++i) {
        _gamepads[i].set_profile(user_settings.get_profile_by_index(i));
    }

    DeviceManager& device_manager = DeviceManager::get_instance();
    device_manager.initialize_driver(user_settings.get_current_driver(), _gamepads);
}

void pico_w::run() {
    multicore_reset_core1();

    // Initialize USB before starting core1 (BT). If BT FW download hangs, the host can
    // still enumerate and run XSM3 auth; core1 runs Bluetooth in parallel.
    DeviceDriver* device_driver = DeviceManager::get_instance().get_driver();
    tud_init(BOARD_TUD_RHPORT);
    printf("USB init done\n");

    multicore_launch_core1(core1_task);
    printf("Core1 (BT) launched\n");

    uint32_t tid_gp_check = TaskQueue::Core0::get_new_task_id();
    set_gp_check_timer(tid_gp_check);

    static bool mounted_logged = false;
    while (true) {
        TaskQueue::Core0::process_tasks();

        for (uint8_t i = 0; i < MAX_GAMEPADS; ++i) {
            device_driver->process(i, _gamepads[i]);
            tud_task();
        }
        if (tud_mounted() && !mounted_logged) {
            mounted_logged = true;
            printf("USB configured (host enumerated)\n");
        }
#if MAIN_LOOP_DELAY_US > 0
        sleep_us(MAIN_LOOP_DELAY_US);
#endif
    }
}

// #else // (OGXM_BOARD == PI_PICOW)

// void pico_w::initialize() {}
// void pico_w::run() {}

#endif // (OGXM_BOARD == PI_PICOW)
