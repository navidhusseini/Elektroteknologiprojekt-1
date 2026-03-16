import dearpygui.dearpygui as dpg

dpg.create_context()

def power_callback(sender, app_data):
    is_on = dpg.get_value(sender)
    label = "SYSTEM ON" if is_on else "SYSTEM OFF"
    dpg.set_item_label(sender, label)
    # Her kan du tilføje logik til at deaktivere andre knapper, hvis systemet er slukket

with dpg.window(label="Pro DJ Dashboard", width=1000, height=650, no_move=True):
    
    # TOP BAR
    with dpg.group(horizontal=True):
        dpg.add_text("DJ CONTROL PANEL v2.0", color=(0, 255, 255))
        dpg.add_spacer(width=600)
        dpg.add_checkbox(label="SYSTEM OFF", callback=power_callback, tag="power_btn")

    dpg.add_separator()
    dpg.add_spacer(height=10)

    # MASTER SECTION (Centreret øverst)
    with dpg.child_window(height=100, label="Master"):
        dpg.add_text("MASTER OUTPUT", bullet=True)
        dpg.add_slider_float(label="Main Volume", default_value=0.5, min_value=0, max_value=1, width=400)

    dpg.add_spacer(height=10)

    # DECKS SECTION (Side om side)
    with dpg.group(horizontal=True):
        
        # DECK A
        with dpg.child_window(width=480, height=250, border=True):
            dpg.add_text("DECK A", color=(255, 100, 100))
            dpg.add_combo(["song1.mp3", "song2.mp3", "song3.mp3"], label="Track", width=300)
            
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="PLAY", width=100, height=40)
                dpg.add_button(label="STOP", width=100, height=40)
            
            dpg.add_spacer(height=10)
            dpg.add_slider_float(label="Gain A", default_value=0.7, min_value=0, max_value=1, vertical=False)

        # DECK B
        with dpg.child_window(width=480, height=250, border=True):
            dpg.add_text("DECK B", color=(100, 100, 255))
            dpg.add_combo(["song4.mp3", "song5.mp3", "song6.mp3"], label="Track", width=300)
            
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="PLAY", width=100, height=40)
                dpg.add_button(label="STOP", width=100, height=40)
            
            dpg.add_spacer(height=10)
            dpg.add_slider_float(label="Gain B", default_value=0.7, min_value=0, max_value=1)

    dpg.add_spacer(height=10)

    # MIXER & LED SECTION
    with dpg.group(horizontal=True):
        # Mixer (Crossfader)
        with dpg.child_window(width=480, height=150):
            dpg.add_text("CROSSFADER")
            dpg.add_slider_float(label="", default_value=0.5, min_value=0, max_value=1, width=450)
            dpg.add_text("A <--------------------------> B", indent=80)

        # LED Status
        with dpg.child_window(width=480, height=150):
            dpg.add_text("LED STATUS INDICATORS")
            with dpg.group(horizontal=True):
                for i in range(1, 5):
                    dpg.add_checkbox(label=f"LED {i}")

# Tema og Styling (Gør det mørkt og professionelt)
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 80))
        dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 40, 90))

dpg.bind_theme(global_theme)

dpg.create_viewport(title="Professional DJ Controller", width=1020, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()