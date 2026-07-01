# Stone Calculator Telegram Bot 🪨

A Telegram bot designed to calculate the weight and surface area of stone materials for business orders. 
*Note: The calculations assume all items are rectangular cuboids.*

## 🌟 Features

* **Material Catalog:** Built-in density values for various stones (Basalt, Gabbro, Labradorite, and various Granites).
* **Cart System:** Add multiple details to a single order and get a comprehensive final summary (total weight, clean area, and area with a +15% production margin).
* **Admin Dashboard:** Hidden `/stats` command to track the number of unique clients and total calculated details.
* **Feedback System:** Users can report issues or leave feedback directly to the admin via the `/help` command.
* **Order Management:** Users can instantly reset and cancel their current calculation at any time using the `/over` command.

## 🛠 Technologies Used

* Python 3
* [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (Telebot)

## 🚀 Quick Start

1. Clone this repository to your local machine.
2. Install the required library:
   bash
   pip install pyTelegramBotAPI
3. Open program.py and replace the placeholders with your actual credentials:

TOKEN = "YOUR_BOT_TOKEN"

ADMIN_ID = YOUR_TELEGRAM_ID

4. Run the bot:

Bash
python program.py
