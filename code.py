# Credit given to John Park <https://learn.adafruit.com/users/johnpark>
# at Adafruit for original code and art assets.
# https://learn.adafruit.com/halloween-countdown-display-matrix/code-the-halloween-countdown
# ** No original license provided **

import time
import board
import gc
from adafruit_matrixportal.matrixportal import MatrixPortal
import terminalio

SYNCHRONIZE_CLOCK = True
POLL_DURATION = 5
UPDATE_DURATION = 60 * 5
SCROLL_DELAY = 0.06

# --- Display setup ---
matrixportal = MatrixPortal(
    status_neopixel=board.NEOPIXEL,
    debug=False,
    height=64,
    width=64,
    bit_depth=2,
    serpentine=True,
    tile_rows=2)

title = ''
last_update = 0

matrixportal.add_text(
    text_font=terminalio.FONT,
    text_scale=.4,
    scrolling=False,
    text_position=(12, (matrixportal.graphics.display.height // 2) - 12),
)

matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 2) + 6),
    scrolling=True
)

matrixportal.add_text(
    text_font=terminalio.FONT,
    text_scale=.4,
    scrolling=False,
    text_position=(24, (matrixportal.graphics.display.height // 2) - 24),
)


def set_next_frame(reference_time):
    matrixportal.network.connect()

    # pylint: disable=global-statement
    global title
    global last_update

    sessions = []
    try:
        # Tautulli location. REPLACE WITH YOUR OWN
        api_url = "http://192.168.86.32:8181/api/v2?apikey=API_KEY&cmd=get_activity"
        reply = matrixportal.network._wifi.requests.get(api_url, timeout=10)
        if reply.status_code == 200:
            response = reply.json().get('response')
            data = response.get('data')
            sessions = data.get('sessions')
        # now clean up
        reply.close()
        reply = None
    except:
        print('Unable to fetch or parse')

    gc.collect()
    if len(sessions) > 0:
        print('Active sessions')
        for session in sessions:
            is_home_user = session.get('is_home_user') == 1
            full_title = session.get('full_title')
            #grandparent_title = session.get('grandparent_title')

            if is_home_user == True:
                matrixportal.set_text('NOW', 2)
                matrixportal.set_text('PLAYING', 0)
                print('Home session is running')
                title = full_title
                matrixportal.set_text(title, 1)
                matrixportal.scroll_text(SCROLL_DELAY)
                # if title != full_title:
                #     title = full_title
                #     last_update = reference_time
                #     matrixportal.set_text('Now playing %s' % title, 1)
                #     matrixportal.scroll_text(SCROLL_DELAY)
                # else:
                #     if reference_time < last_update + UPDATE_DURATION:
                #         print('Skipping this update')
                #     else:
                #         print('Planning to update text to %s' % title)
                #         last_update = reference_time
                #         matrixportal.set_text('You\'re watching %s' % title, 1)
                #         matrixportal.scroll_text(SCROLL_DELAY)

    else:
        print('Resetting text')
        matrixportal.set_text('', 0)
        matrixportal.set_text('', 1)
        matrixportal.set_text('', 2)

    matrixportal.set_background(0)


# Simulate the delay in case fetching time is fast
matrixportal.set_text("Booting..", 1)
matrixportal.scroll_text(SCROLL_DELAY)
start_time = time.monotonic()
if SYNCHRONIZE_CLOCK:
    matrixportal.get_local_time()
    matrixportal.set_text('', 1)

while time.monotonic() < start_time + POLL_DURATION:
    pass

while True:
    set_next_frame(time.monotonic())
    time.sleep(POLL_DURATION)
