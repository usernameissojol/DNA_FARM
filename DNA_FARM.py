import logging
import random
import string
import os
import time
import re
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import hashlib
from datetime import datetime  # Import datetime for timestamp

# Setup logging
logging.basicConfig(level=logging.INFO)

# Your API ID and hash from my.telegram.org
api_id = "26887272"  # Replace with your API ID
api_hash = 'eb04e1a500856df3405d58964197e29a'  # Replace with your API hash````````````````````````
bot_token = '8176686979:AAEVO4c4gBXAF5fQnXtJJL8m9_1i03bOjek'  # Replace with your actual bot token

# Create the client and connect
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# File for storing user data
database_file = 'Database.txt'
activity_log_file = 'activity_log.txt'  # New file for activity log

#Help Menu.
@client.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    help_text = (
        "Available Commands:\n"
        "/start - Start the bot\n"
        "/register - Register a new account\n"
        "/login - Log in to your account\n"
        # Add more commands as needed
    )
    await event.respond(help_text)


#Admin Pannel.
admin_id=5289529090
@client.on(events.NewMessage(pattern='/admin'))
async def admin_panel(event):
    user_id = event.sender_id
    if user_id == admin_id:
        # Display admin panel options
        buttons = [
            [Button.text("📊 View User Data")],
            [Button.text("📥 View Withdrawal Requests")],
            [Button.text("🔙 Back to Main Menu")]
        ]
        await event.respond('Welcome to the Admin Panel! Choose an option:', buttons=buttons)
        logging.info(f'Admin panel accessed by {user_id}')
    else:
        await event.respond("🚫 You do not have permission to access the admin panel.")
        logging.warning(f'Unauthorized access attempt to admin panel by {user_id}')

@client.on(events.NewMessage)
async def handle_admin_actions(event):
    sender_id = event.sender_id

    if sender_id == admin_id:
        if event.raw_text == "📊 View User Data":
            # Retrieve and display user data
            with open(database_file, 'r') as f:
                data = f.read()
            await event.respond(f"User Data:\n{data}")

        elif event.raw_text == "📥 View Withdrawal Requests":
            # Display withdrawal requests (implement logic to read from a file or database)
            await event.respond("📥 Here are the withdrawal requests...\n(Implement logic to display requests here.)")

        elif event.raw_text == "🔙 Back to Main Menu":
            buttons = [
                [Button.text('💻 Register', resize=True)],
                [Button.text('🔑 Login', resize=True)]
            ]
            await event.respond('Welcome to the Banking Bot! Please choose an option:', buttons=buttons)

# Helper function to log activities
def log_activity(uid, action):
    """Log user activity with a timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(activity_log_file, 'a') as f:
        f.write(f"UID: {uid} | Action: {action} | DateTime: {timestamp}\n")

# Helper functions to read/write from the text file
def save_user_to_file(uid, name, email, phone, password, Balance, Referal):
    """Save user data to a text file in a readable format."""
    with open(database_file, 'a') as f:
        f.write(f"UID: {uid}\nName: {name}\nEmail: {email}\nPhone: {phone}\nPassword: {password}\nBalance: {Balance}\nReferal: {Referal}\n---\n")

def email_exists(email):
    """Check if the email already exists in the text file."""
    if not os.path.exists(database_file):
        return False
    with open(database_file, 'r') as f:
        return email in f.read()

def phone_exists(phone):
    """Check if the phone number already exists in the text file."""
    if not os.path.exists(database_file):
        return False
    with open(database_file, 'r') as f:
        return phone in f.read()

# Helper functions for validation and UID generation
def generate_uid():
    """Generates a unique 10-digit UID for users."""
    return ''.join(random.choices(string.digits, k=10))

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validates the email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    """Validates the phone format (10 digits)."""
    return re.match(r"^\d{10}$", phone)
from telethon import Button
import asyncio

# Create the main buttons, with control over whether to show the "Start Farming" button
def create_main_buttons(show_farming_button=True):
    buttons = []

    if show_farming_button:
        buttons.append([Button.text("🌾 Start Farming")])

    buttons.extend([
        [Button.text("📈 Check Status"), Button.text("🗒️ Task for Today")],
        [Button.text("🔗 Share Referral Link")],
        [Button.text("💵 Add Money Request"), Button.text("💸 Send Money")],  # Banking related
        [Button.text("🏧 Withdraw"), Button.text("📋 More Options")],         # Banking related
        [Button.text("💰 Check Balance"), Button.text("📊 Transaction History")],  # Banking related
        [Button.text("🔄 Transfer Funds"), Button.text("🔐 Account Settings")]  # Banking related
    ])
    
    return buttons
# User states to keep track of registration progress
user_states = {}

# Define the required channel username
required_channel = 'DNA_FARM_BOT'  # Replace with your channel

# Helper function to check if the user has joined the required channel
async def is_user_in_channel(client, user_id):
    try:
        participants = await client(GetParticipantsRequest(
            channel=required_channel,
            filter=ChannelParticipantsSearch(''),
            offset=0,
            limit=100,
            hash=0
        ))
        for participant in participants.users:
            if participant.id == user_id:
                return True
        return False
    except Exception as e:
        logging.error(f"Error checking channel membership: {e}")
        return False

# Handler for the /start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id

    # Check if the user has joined the required channel
    if await is_user_in_channel(client, user_id):
        # Check if user is already registered
        if user_registered(user_id):  # Check if user is already registered
            await event.respond('🚫 You are already registered. Please login using your UID and password.', 
                                buttons=[Button.text('🔑 Login', resize=True)])
        else:
            # Show registration options
            buttons = [
                [Button.text('💻 Register', resize=True)],
                [Button.text('🔑 Login', resize=True)]
            ]
            await event.respond('Welcome to the Banking Bot! Please choose an option:', buttons=buttons)
            logging.info(f'Start command received from {user_id}')
    else:
        # Prompt the user to join the required channel
        await event.respond(f'🚫 You need to join the [DNA Farm](https://t.me/{required_channel}) before registering.',
                            buttons=[Button.text('Check if Joined', resize=True)], parse_mode='markdown')
        logging.info(f'User {user_id} prompted to join the required channel')

# Helper function to check if the user is already registered
def user_registered(uid):
    """Check if the user is already registered based on UID."""
    if not os.path.exists(database_file):
        return False
    with open(database_file, 'r') as f:
        return str(uid) in f.read()


# Handler for registration steps
@client.on(events.NewMessage)
async def handle_registration(event):
    sender_id = event.sender_id

    # Handle the "Check if Joined" button
    if event.raw_text == "Check if Joined":
        if await is_user_in_channel(client, sender_id):
            if user_registered(sender_id):  # Check if user is already registered
                await event.respond('🚫 You are already registered. Please login using your UID and password.', 
                                    buttons=[Button.text('🔑 Login', resize=True)])
            else:
                buttons = [
                    [Button.text('💻 Register', resize=True)],
                    [Button.text('🔑 Login', resize=True)]
                ]
                await event.respond('🎉 You have successfully joined the channel! Please choose an option:', buttons=buttons)
        else:
            await event.respond(f'🚫 You still need to join the [official channel](https://t.me/{required_channel}) before registering.',
                                buttons=[Button.text('Check if Joined', resize=True)], parse_mode='markdown')

    # Start registration process (only if not already registered)
    elif event.raw_text == "💻 Register":
        if await is_user_in_channel(client, sender_id):
            if user_registered(sender_id):  # Check if user is already registered
                await event.respond('🚫 You are already registered. Please login using your UID and password.', 
                                    buttons=[Button.text('🔑 Login', resize=True)])
            else:
                user_states[sender_id] = {"step": "name"}
                await event.respond('📝 Please provide your full name:')
                logging.info(f'Registration started by {sender_id}')
        else:
            await event.respond(f'🚫 You need to join the [official channel](https://t.me/{required_channel}) before registering.', parse_mode='markdown')


    # Start registration process
    elif event.raw_text == "💻 Register":
        if await is_user_in_channel(client, sender_id):
            user_states[sender_id] = {"step": "name"}
            await event.respond('📝 Please provide your full name:')
            logging.info(f'Registration started by {sender_id}')
        else:
            await event.respond(f'🚫 You need to join the [official channel](https://t.me/{required_channel}) before registering.', parse_mode='markdown')

    # Collect name
    elif sender_id in user_states and user_states[sender_id]["step"] == "name":
        name = event.raw_text.strip()
        if not name:
            await event.respond("🚫 This is not valid. Please provide your full name:")
            return
        user_states[sender_id]["name"] = name
        user_states[sender_id]["step"] = "email"
        await event.respond('📧 Please provide your email:')

    # Collect email and validate
    elif sender_id in user_states and user_states[sender_id]["step"] == "email":
        email = event.raw_text.strip()
        if not validate_email(email):
            await event.respond("🚫 Invalid email format. Please provide a valid email:")
            return
        if email_exists(email):
            await event.respond("🚫 Email already exists. Please use a different email:")
            return
        user_states[sender_id]["email"] = email
        user_states[sender_id]["step"] = "phone"
        await event.respond('📞 Please provide your phone number (10 digits):')

    # Collect phone and validate
    elif sender_id in user_states and user_states[sender_id]["step"] == "phone":
        phone = event.raw_text.strip()
        if not validate_phone(phone):
            await event.respond("🚫 Invalid phone number. Please provide a valid 10-digit phone number:")
            return
        if phone_exists(phone):
            await event.respond("🚫 Phone number already exists. Please use a different number:")
            return
        user_states[sender_id]["phone"] = phone
        user_states[sender_id]["step"] = "password"
        await event.respond('🔒 Please provide a password (minimum 6 characters):')

    # Collect password
    # Collect password
    elif sender_id in user_states and user_states[sender_id]["step"] == "password":
        password = event.raw_text.strip()
        if len(password) < 6:
            await event.respond("🚫 Password too short. Please provide a password with at least 6 characters:")
            return
        user_states[sender_id]["password"] = password
        # Use the sender_id as the UID directly
        uid = sender_id  # Use Telegram user ID as UID
        hashed_password = hash_password(password)
        save_user_to_file(uid, user_states[sender_id]["name"], user_states[sender_id]["email"], user_states[sender_id]["phone"], hashed_password, Balance=0, Referal=0)
        log_activity(uid, 'Registration')  # Log the registration activity
        await event.respond(f'🎉 Registration successful! Your UID is: {uid}\n\n'
                            '🔔 **Read This Notice Attentively**\n\n'
                            f'🚨 This is Your Account Number: {uid}\n'
                            '🚫 Don\'t share your Account Number or password with anyone.\n'
                            '💾 Secretly save this and don\'t forget it.\n'
                            '🆘 If you face any problem or need any help, contact Support Team. (@DNA_FARM_BOT).\n'
                            'You can now login using your UID and password.',
                            buttons=[Button.text('/start', resize=True)])
        logging.info(f'User {sender_id} successfully registered with UID {uid}')
        del user_states[sender_id]  # Clear user state after registration

    # Handle login process
    elif event.raw_text == "🔑 Login":
        user_states[sender_id] = {"step": "login_uid"}
        await event.respond('🔑 Please provide your UID to login:')

    # Collect UID for login
    elif sender_id in user_states and user_states[sender_id]["step"] == "login_uid":
        uid = str(event.raw_text.strip())  # Ensure UID is treated as a string
        user_states[sender_id]["uid"] = uid
        user_states[sender_id]["step"] = "login_password"
        await event.respond('🔒 Please provide your password:')

    # Collect password for login
    elif sender_id in user_states and user_states[sender_id]["step"] == "login_password":
        password = event.raw_text.strip()
        hashed_password = hash_password(password)

        # Check if UID and password match
        with open(database_file, 'r') as f:
            data = f.read()

        # Updated regex pattern to handle more flexible spacing and line breaks
        user_data = re.findall(r"UID: (.*?)\nName: (.*?)\nEmail: (.*?)\nPhone: (.*?)\nPassword: (.*?)\nBalance: (.*?)\nReferal: (.*?)\n---", data)

        login_successful = False
        username = None

        # Loop through user data and check for matching UID and password
        for uid, name, email, phone, stored_password, balance, referral in user_data:
            if uid == str(user_states[sender_id]["uid"]) and stored_password == hashed_password:  # Ensure UID is treated as a string
                login_successful = True
                username = name  # Store the username for later use
                break

        if login_successful:
            log_activity(user_states[sender_id]["uid"], 'Login')  # Log the login activity
            await event.respond(f'🎉 <b>Authenticated! Welcome back, {username}!</b>', parse_mode='html', buttons=create_main_buttons())
            logging.info(f'User {sender_id} logged in successfully with UID {user_states[sender_id]["uid"]}')
            del user_states[sender_id]  # Clear user state after login
        else:
            await event.respond('🚫 Invalid UID or password. Please try again.')
            logging.info(f'User {sender_id} failed to login with UID {user_states[sender_id]["uid"]}')
# Function to handle balance checking
async def check_balance(event):
    user_uid = str(event.sender_id)  # Extract the user's Telegram ID
    
    # Open the database file
    with open('Database.txt', 'r') as f:
        lines = f.readlines()
    
    # Initialize variables to track user data
    current_uid = None
    balance = None

    # Parse through the file
    for line in lines:
        line = line.strip()  # Remove any extra whitespace or newline characters
        
        if line.startswith("UID: "):
            current_uid = line.split(": ")[1]  # Extract the UID
            
        elif line.startswith("Balance: ") and current_uid == user_uid:
            balance = line.split(": ")[1]  # Extract the balance
            break
        
        elif line == "---":
            current_uid = None  # Reset UID when encountering a separator (---)
    
    # Respond to the user with their balance
    if balance is not None:
        await event.respond(f"💰 Your current balance is {balance}")
    else:
        await event.respond("⚠️ Error: Could not find your balance. Please try again.")

# Send money Logic:
# Dictionary to temporarily store user data (amount and recipient)
pending_transactions = {}

# Function to handle sending money
async def send_money(event, amount, recipient_uid):
    sender_uid = str(event.sender_id)  # Extract the sender's Telegram ID
    
    # Open the database file and read the contents
    with open('Database.txt', 'r') as f:
        lines = f.readlines()

    # Initialize variables for sender and recipient balances
    sender_balance = None
    recipient_balance = None
    sender_line_index = None
    recipient_line_index = None

    # Parse the database to find sender and recipient data
    for i, line in enumerate(lines):
        line = line.strip()

        # Find sender's data
        if line.startswith(f"UID: {sender_uid}"):
            while not lines[i].startswith("Balance: "):
                i += 1
            sender_balance = int(lines[i].split(": ")[1])  # Extract sender balance
            sender_line_index = i
        
        # Find recipient's data
        if line.startswith(f"UID: {recipient_uid}"):
            while not lines[i].startswith("Balance: "):
                i += 1
            recipient_balance = int(lines[i].split(": ")[1])  # Extract recipient balance
            recipient_line_index = i
        
        # Stop searching once both sender and recipient are found
        if sender_balance is not None and recipient_balance is not None:
            break
    
    # Check if both sender and recipient were found
    if sender_balance is None:
        await event.respond("⚠️ Error: Could not find your account.")
        return
    if recipient_balance is None:
        await event.respond(f"⚠️ Error: Could not find recipient with UID {recipient_uid}.")
        return

    # Check if the sender has enough balance
    if sender_balance < amount:
        await event.respond("⚠️ Error: You don't have enough balance to send that amount.")
        return

    # Update balances
    sender_balance -= amount
    recipient_balance += amount

    # Update the database file with new balances
    lines[sender_line_index] = f"Balance: {sender_balance}\n"
    lines[recipient_line_index] = f"Balance: {recipient_balance}\n"
    
    with open('Database.txt', 'w') as f:
        f.writelines(lines)

    # Respond to the sender
    await event.respond(f"✅ Success! You have sent {amount} to UID: {recipient_uid}.\n💰 Your new balance is {sender_balance}.")
    
    # Notify the recipient
    try:
        recipient_telegram_id = int(recipient_uid)  # Assuming recipient UID is their Telegram ID
        await client.send_message(recipient_telegram_id, f"💸 You have received {amount} from UID: {sender_uid}.\n💰 Your new balance is {recipient_balance}.")
    except Exception as e:
        print(f"Error notifying recipient: {e}")  # Log the error if recipient notification fails

    
import logging
import asyncio
from telethon import TelegramClient, events, Button
from datetime import datetime
            # Helper function to log activities
def log_activity(uid, action):
    """Log user activity with a timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(activity_log_file, 'a') as f:
        f.write(f"UID: {uid} | Action: {action} | DateTime: {timestamp}\n")

# Helper function to update user balance in the database file
def update_user_balance(user_id, amount):
    user_found = False  # To track if the user was found and updated
    new_lines = []  # To store the updated lines for writing back to the file
    
    # Open the database file and read the content
    with open('Database.txt', 'r') as f:
        lines = f.readlines()  # Read all lines into a list
    
    # Iterate through the lines and update the user's balance
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(f"UID: {user_id}"):  # Check if this is the user we are looking for
            user_found = True
            new_lines.append(line)  # Append the UID line unchanged
            i += 1  # Move to the next line
            
            # Copy the next few lines (Name, Email, etc.) unchanged until we reach the Balance line
            while i < len(lines) and not lines[i].startswith("Balance:"):
                new_lines.append(lines[i])
                i += 1
            
            # Now we are at the Balance line, update the balance
            if lines[i].startswith("Balance:"):
                balance_line = lines[i]
                balance = int(balance_line.split(':')[1].strip())  # Get the current balance
                balance += amount  # Add the earned amount to the balance
                new_lines.append(f"Balance: {balance}\n")  # Write the updated balance
                i += 1  # Move to the next line
                
            # Copy the remaining lines (Referral and the separator) unchanged
            while i < len(lines) and not lines[i].startswith("UID:"):
                new_lines.append(lines[i])
                i += 1
        else:
            # If it's not the correct user, just copy the line as is
            new_lines.append(line)
            i += 1
    
    # Write the updated lines back to the file
    with open('Database.txt', 'w') as f:
        f.writelines(new_lines)
    
    if user_found:
        print(f"Balance updated for user {user_id}.")
    else:
        print(f"User with UID {user_id} not found.")

#Check Status.
def check_user_status(user_id):
    user_found = False  # Flag to indicate if user is found
    user_info = {}  # Dictionary to store user information

    # Open the database file and read the content
    with open('Database.txt', 'r') as f:
        lines = f.readlines()
    
    # Iterate through the lines to find the user
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(f"UID: {user_id}"):  # Check if this line contains the target UID
            user_found = True
            user_info['UID'] = user_id
            i += 1  # Move to the next line
            
            # Continue to retrieve the rest of the user information
            while i < len(lines) and not lines[i].startswith("UID:") and not lines[i].startswith("---"):
                if lines[i].startswith("Name:"):
                    user_info['Name'] = lines[i].split(":")[1].strip()
                elif lines[i].startswith("Email:"):
                    user_info['Email'] = lines[i].split(":")[1].strip()
                elif lines[i].startswith("Phone:"):
                    user_info['Phone'] = lines[i].split(":")[1].strip()
                elif lines[i].startswith("Balance:"):
                    user_info['Balance'] = int(lines[i].split(":")[1].strip())
                elif lines[i].startswith("Referal:"):
                    user_info['Referral'] = int(lines[i].split(":")[1].strip())
                # Move to the next line
                i += 1
            break  # Stop after finding the user details
        i += 1
    
    # Handle the case where the user is not found
    if user_found:
        return user_info
    else:
        return f"User with UID {user_id} not found."

import asyncio
from telethon import Button 
# Handle button actions after successful login
import asyncio
@client.on(events.NewMessage)
async def handle_button_actions(event):
    sender_id = event.sender_id

    if event.raw_text == "🌾 Start Farming":
        # Send message without the "Start Farming" button
        await event.respond(
            "🌾 Farming started! You will earn points in 1 minute.",
            buttons=create_main_buttons(show_farming_button=False)  # Hide the farming button
        )
        log_activity(sender_id, "Started Farming")

        # Wait for 1 minute
        await asyncio.sleep(60)

        # Add points to the user's balance
        update_user_balance(sender_id, 10)
        
        # Send another message with the "Start Farming" button visible again
        await event.respond(
            "🌾 Farming completed! You have earned 10 points.",
            buttons=create_main_buttons(show_farming_button=True)  # Show the farming button again
        )



    elif event.raw_text == "📈 Check Status":
        sender_id = event.sender_id  # Assuming you want to check status based on sender's UID
        user_status = check_user_status(sender_id)  # Call the function to check status

        # Format the response based on the returned status
        if isinstance(user_status, dict):  # If user info is found
            status_message = (
                f"📊 User Status:\n"
                f"Name: {user_status['Name']}\n"
                f"Email: {user_status['Email']}\n"
                f"Phone: {user_status['Phone']}\n"
                f"Balance: {user_status['Balance']}\n"
                f"Referral Count: {user_status['Referral']}"
            )
        else:  # If user not found
            status_message = user_status

        await event.respond(status_message)  # Send the status back to the user


    elif event.raw_text == "🗒️ Task for Today":
        await event.respond("🗒️ Here are your tasks for today...")
        # Implement task retrieval logic

    elif event.raw_text == "🔗 Share Referral Link":
        await event.respond("🔗 Your referral link: [Your Referral Link]")
        # Implement referral link sharing logic

    elif event.raw_text == "💵 Add Money Request":
        await event.respond("💵 Please specify the amount to request.")
        # Implement add money request logic

    elif event.raw_text == "💸 Send Money":
        await event.respond("💸 Please specify the amount to send.")
        pending_transactions[event.sender_id] = {"stage": "awaiting_amount"}
    
    elif event.sender_id in pending_transactions:
        if pending_transactions[event.sender_id]["stage"] == "awaiting_amount":
            try:
                amount = int(event.raw_text)  # Parse the amount
                pending_transactions[event.sender_id]["amount"] = amount
                pending_transactions[event.sender_id]["stage"] = "awaiting_recipient"
                await event.respond("📥 Please provide the recipient's UID.")
            except ValueError:
                await event.respond("⚠️ Please enter a valid number for the amount.")
        
        elif pending_transactions[event.sender_id]["stage"] == "awaiting_recipient":
            recipient_uid = event.raw_text
            amount = pending_transactions[event.sender_id]["amount"]
            
            # Proceed to send money
            await send_money(event, amount, recipient_uid)
            
            # Clear pending transaction
            del pending_transactions[event.sender_id]
            
        elif pending_transactions[event.sender_id]["stage"] == "awaiting_recipient":
            recipient_uid = event.raw_text
            amount = pending_transactions[event.sender_id]["amount"]
            
            # Proceed to send money
            await send_money(event, amount, recipient_uid)
            
            # Clear pending transaction
            del pending_transactions[event.sender_id]

        # Implement send money logic

    elif event.raw_text == "🏧 Withdraw":
        # Available withdrawal platforms
        await event.respond("1.Binance\n2.Bitget\n3.Kucoin\n4.Gate.io\n🏧 This feature is coming soon! Stay tuned for updates.")
        # Implement withdrawal logic

    elif event.raw_text == "📋 More Options":
        await event.respond("📋 Here are more options for you...")
        # Implement more options logic

    elif event.raw_text == "💰 Check Balance":
        await check_balance(event)
        
        # Implement balance checking logic

    elif event.raw_text == "📊 Transaction History":
        await event.respond("📊 Here is your transaction history...")
        # Implement transaction history retrieval logic

    elif event.raw_text == "🔄 Transfer Funds":
        await event.respond("🔄 Please specify the amount and recipient for transfer.")
        # Implement fund transfer logic

    elif event.raw_text == "🔐 Account Settings":
        await event.respond("🔐 Here you can manage your account settings.")
        # Implement account settings management logic

# Start the Telegram client
client.start()
logging.info("Bot is running...")
client.run_until_disconnected()