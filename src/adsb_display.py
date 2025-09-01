import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

from fetch import fetch_aircraft_within_radius
from aircraft import Aircraft, parse_aircraft, DisplayPriority
from temperature import get_latest_room_temperature


def get_aircraft_list() -> list[Aircraft] | None:
    raw_ac = fetch_aircraft_within_radius(radius=100)
    if raw_ac is None:
        raise SystemExit("No aircraft data fetched.")
    return parse_aircraft(raw_ac)


class ADSBDisplay:
    def __init__(self, fb_device="/dev/fb1"):
        self.fb_device = fb_device
        self.width = 320
        self.height = 240

        # Load fonts
        try:
            self.font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf", 16
            )
            self.font_aircraft = ImageFont.truetype(
                "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf", 12
            )
        except OSError:
            self.font_small = ImageFont.load_default()
            self.font_aircraft = ImageFont.load_default()

        self.last_update = datetime.now() - timedelta(minutes=31)

    def draw_frame_to_fb(self, image):
        """Convert PIL image to RGB565 and write to framebuffer"""
        rgb_image = image.convert("RGB")
        pixels = list(rgb_image.getdata())

        fb_data = bytearray(self.width * self.height * 2)

        for i, (r, g, b) in enumerate(pixels):
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            fb_data[i * 2] = rgb565 & 0xFF
            fb_data[i * 2 + 1] = (rgb565 >> 8) & 0xFF

        with open(self.fb_device, "wb") as fb:
            fb.write(fb_data)

    def create_frame(self, temp: str, aircraft: list):
        """Create frame with temperature and aircraft list"""
        image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        time_now = datetime.now().strftime("%H:%M %d/%m/%Y")
        temp_text = f"{temp:0.1f} C - {time_now}"
        draw.text((5, 5), temp_text, font=self.font_small, fill=(255, 255, 255))

        # Aircraft list starting at y=25
        y_pos = 25
        aircraft_to_show = []

        for priority in [
            DisplayPriority.HIGH,
            DisplayPriority.MEDIUM,
            DisplayPriority.LOW,
        ]:
            for ac in aircraft:
                if ac.priority == priority:
                    aircraft_to_show.append(ac)
                    if len(aircraft_to_show) >= 12:
                        break
            if len(aircraft_to_show) >= 12:
                break

        for i, ac in enumerate(aircraft_to_show[:12]):  # Limit to 12
            if ac.priority == DisplayPriority.HIGH:
                color = (255, 0, 0)
            elif ac.priority == DisplayPriority.MEDIUM:
                color = (255, 255, 0)
            else:
                color = (0, 255, 0)

            # Format aircraft info
            dist = f"{ac.distance_km:.1f}km" if ac.distance_km is not None else "?km"
            ac_type = ac.aircraft_type or "?"
            alt = (
                f"{int(ac.altitude_baro)}ft" if ac.altitude_baro is not None else "?ft"
            )
            speed = (
                f"{int(ac.ground_speed)}kt" if ac.ground_speed is not None else "?kt"
            )

            if ac.registration:
                registration = ac.registration
            elif ac.flight_number:
                registration = ac.flight_number
            else:
                registration = "?"

            aircraft_text = f"{dist} {ac_type} {registration} {alt} {speed}"
            draw.text((5, y_pos), aircraft_text, font=self.font_aircraft, fill=color)
            y_pos += 18  # Line spacing

        return image

    def run(self):
        """Main display loop"""
        print("Starting ADSB aircraft display...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                now = datetime.now()

                # Update every 30 seconds
                if now - self.last_update > timedelta(seconds=30):
                    try:
                        temp = get_latest_room_temperature()
                        aircraft = get_aircraft_list()

                        frame = self.create_frame(temp, aircraft)
                        self.draw_frame_to_fb(frame)

                        self.last_update = now
                        print(f"Display updated: {temp}°C, {len(aircraft)} aircraft")

                    except Exception as e:
                        print(f"Update failed: {e}")

                time.sleep(5)  # Check every 5 seconds

        except KeyboardInterrupt:
            print("\nDisplay stopped")
