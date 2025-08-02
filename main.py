import asyncio
import json
import hashlib
import threading
import time
import os
import base64
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.carousel import Carousel
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.stencilview import StencilView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform
from kivy.animation import Animation
from kivy.effects.scroll import ScrollEffect
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.logger import Logger
from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import qrcode
from io import BytesIO

# Define UUIDs for our custom service and characteristics
SERVICE_UUID = "0000FFE0-0000-1000-8000-00805F9B34FB"
TX_CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"  # For receiving data
RX_CHAR_UUID = "0000FFE2-0000-1000-8000-00805F9B34FB"  # For sending data

# Color scheme
PRIMARY_COLOR = (0.2, 0.6, 0.9, 1)  # Blue
SECONDARY_COLOR = (0.1, 0.4, 0.7, 1)  # Darker blue
ACCENT_COLOR = (0.9, 0.2, 0.2, 1)  # Red
BACKGROUND_COLOR = (0.95, 0.95, 0.95, 1)  # Light gray
TEXT_COLOR = (0.1, 0.1, 0.1, 1)  # Dark gray
LIGHT_TEXT_COLOR = (0.7, 0.7, 0.7, 1)  # Light gray
SUCCESS_COLOR = (0.2, 0.8, 0.4, 1)  # Green


class AnimatedButton(Button):
    def __init__(self, **kwargs):
        super(AnimatedButton, self).__init__(**kwargs)
        self.background_color = PRIMARY_COLOR
        self.color = (1, 1, 1, 1)
        self.bind(on_press=self.animate_press)

    def animate_press(self, instance):
        anim = Animation(scale=0.95, duration=0.1) + Animation(scale=1.0, duration=0.1)
        anim.start(self)


class AnimatedLabel(Label):
    def __init__(self, **kwargs):
        super(AnimatedLabel, self).__init__(**kwargs)
        self.color = TEXT_COLOR
        self.bind(size=self.update_text_size)

    def update_text_size(self, instance, value):
        self.text_size = (self.width - dp(10), None)
        self.halign = 'left'
        self.valign = 'middle'


class Block:
    def __init__(self, index: int, previous_hash: str, timestamp: float, data: str, nonce: int = 0,
                 sender_id: str = None, recipient_id: str = None, message_type: str = "text",
                 file_data: str = None, file_name: str = None, encryption_key: str = None,
                 expiration_time: float = None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_type = message_type  # text, file, image, etc.
        self.file_data = file_data  # Base64 encoded file data
        self.file_name = file_name
        self.encryption_key = encryption_key
        self.expiration_time = expiration_time  # For disappearing messages
        self.status = "sent"  # sent, delivered, read

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "nonce": self.nonce,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "file_data": self.file_data,
            "file_name": self.file_name,
            "encryption_key": self.encryption_key,
            "expiration_time": self.expiration_time
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_json(self) -> str:
        return json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "nonce": self.nonce,
            "hash": self.hash,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "file_data": self.file_data,
            "file_name": self.file_name,
            "encryption_key": self.encryption_key,
            "expiration_time": self.expiration_time,
            "status": self.status
        })

    @staticmethod
    def from_json(json_str: str) -> 'Block':
        data = json.loads(json_str)
        block = Block(
            data['index'],
            data['previous_hash'],
            data['timestamp'],
            data['data'],
            data['nonce'],
            data.get('sender_id'),
            data.get('recipient_id'),
            data.get('message_type', 'text'),
            data.get('file_data'),
            data.get('file_name'),
            data.get('encryption_key'),
            data.get('expiration_time')
        )
        block.hash = data['hash']
        block.status = data.get('status', 'sent')
        return block


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_blocks = []  # For store-and-forward

    def create_genesis_block(self) -> Block:
        return Block(0, "0", datetime.now().timestamp(), "Genesis Block")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, new_block: Block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def proof_of_work(self, block: Block) -> Block:
        while not block.hash.startswith('0' * self.difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def add_pending_block(self, block: Block):
        """Add a block to pending list for store-and-forward"""
        self.pending_blocks.append(block)

    def get_pending_blocks_for_recipient(self, recipient_id: str) -> List[Block]:
        """Get all pending blocks for a specific recipient"""
        return [block for block in self.pending_blocks if block.recipient_id == recipient_id]

    def remove_pending_blocks(self, blocks: List[Block]):
        """Remove delivered blocks from pending list"""
        for block in blocks:
            if block in self.pending_blocks:
                self.pending_blocks.remove(block)


class CryptoManager:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.contacts = {}  # contact_id: public_key

    def get_public_key_pem(self) -> str:
        """Get PEM formatted public key"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def add_contact(self, contact_id: str, public_key_pem: str):
        """Add a contact with their public key"""
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        self.contacts[contact_id] = public_key

    def encrypt_message(self, message: str, recipient_id: str) -> Tuple[str, str]:
        """Encrypt a message for a recipient
        Returns: (encrypted_message, encryption_key)
        """
        if recipient_id not in self.contacts:
            raise ValueError(f"Recipient {recipient_id} not in contacts")

        # Generate a random AES key
        aes_key = os.urandom(32)  # 256-bit key

        # Encrypt the message with AES
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CFB(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_message = encryptor.update(message.encode('utf-8')) + encryptor.finalize()

        # Encrypt the AES key with the recipient's public key
        encrypted_key = self.contacts[recipient_id].encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Return base64 encoded encrypted message and key
        return (
            base64.b64encode(iv + encrypted_message).decode('utf-8'),
            base64.b64encode(encrypted_key).decode('utf-8')
        )

    def decrypt_message(self, encrypted_message: str, encryption_key: str) -> str:
        """Decrypt a message"""
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_message)
        encrypted_key = base64.b64decode(encryption_key)

        # Decrypt the AES key with our private key
        aes_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Extract IV and encrypted message
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]

        # Decrypt the message with AES
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CFB(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(encrypted) + decryptor.finalize()

        return decrypted_message.decode('utf-8')

    def sign_data(self, data: str) -> str:
        """Sign data with private key"""
        signature = self.private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, data: str, signature: str, contact_id: str) -> bool:
        """Verify signature from a contact"""
        if contact_id not in self.contacts:
            return False

        try:
            self.contacts[contact_id].verify(
                base64.b64decode(signature),
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


class MessageBubble(BoxLayout):
    def __init__(self, block, is_self=True, device_type=None, **kwargs):
        super(MessageBubble, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = self.minimum_height
        self.padding = [dp(10), dp(5)]
        self.block = block
        self.is_self = is_self
        self.device_type = device_type

        # Device icon
        if not is_self and device_type:
            device_icon = Image(
                source=self.get_device_icon(device_type),
                size_hint=(None, 1),
                width=dp(30),
                mipmap=True
            )
            self.add_widget(device_icon)

        # Message container
        msg_container = BoxLayout(orientation='vertical', size_hint_x=0.8)
        if is_self:
            self.pos_hint = {'right': 1}
            msg_container.pos_hint = {'right': 1}
        else:
            self.pos_hint = {'x': 0}
            msg_container.pos_hint = {'x': 0}

        # Message background
        with msg_container.canvas.before:
            Color(PRIMARY_COLOR[0], PRIMARY_COLOR[1], PRIMARY_COLOR[2], 1) if is_self else Color(0.9, 0.9, 0.9, 1)
            self.rect = RoundedRectangle(pos=msg_container.pos, size=msg_container.size, radius=[dp(10)])

        msg_container.bind(pos=self.update_rect, size=self.update_rect)

        # Message content
        if block.message_type == "text":
            msg_label = AnimatedLabel(
                text=block.data,
                size_hint_y=None,
                height=dp(30)
            )
            msg_label.bind(texture_size=msg_label.setter('size'))
            msg_container.add_widget(msg_label)
        elif block.message_type in ["image", "file"]:
            # File/image preview
            if block.message_type == "image":
                img = AsyncImage(
                    source=block.data,
                    size_hint=(None, None),
                    size=(dp(150), dp(150)),
                    mipmap=True
                )
                msg_container.add_widget(img)

            # File name
            file_label = AnimatedLabel(
                text=block.file_name or "File",
                size_hint_y=None,
                height=dp(20),
                bold=True
            )
            file_label.bind(texture_size=file_label.setter('size'))
            msg_container.add_widget(file_label)

        # Timestamp and status
        info_layout = BoxLayout(size_hint_y=None, height=dp(20))

        timestamp = datetime.fromtimestamp(block.timestamp).strftime("%H:%M")
        time_label = Label(
            text=timestamp,
            color=LIGHT_TEXT_COLOR,
            size_hint_x=0.7,
            font_size=dp(10),
            halign='left'
        )

        # Status icon
        status_icon = "atlas://data/images/defaulttheme/checkbox_on" if block.status == "read" else \
            "atlas://data/images/defaulttheme/checkbox_off" if block.status == "delivered" else \
                "atlas://data/images/defaulttheme/checkbox_blank"

        status_img = Image(
            source=status_icon,
            size_hint=(None, 1),
            width=dp(15)
        )

        info_layout.add_widget(time_label)
        info_layout.add_widget(status_img)
        msg_container.add_widget(info_layout)

        # Expiration timer if disappearing message
        if block.expiration_time and block.expiration_time > time.time():
            remaining = block.expiration_time - time.time()
            timer_label = Label(
                text=f"Disappears in {int(remaining)}s",
                color=ACCENT_COLOR,
                size_hint_y=None,
                height=dp(15),
                font_size=dp(10),
                italic=True
            )
            msg_container.add_widget(timer_label)

            # Start countdown timer
            Clock.schedule_once(lambda dt: self.update_expiration_timer(timer_label, block), 1)

        self.add_widget(msg_container)

        # Animate entrance
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def get_device_icon(self, device_type):
        # Return appropriate icon based on device type
        if device_type == "phone":
            return 'atlas://data/images/defaulttheme/phone'
        elif device_type == "tablet":
            return 'atlas://data/images/defaulttheme/tablet'
        elif device_type == "laptop":
            return 'atlas://data/images/defaulttheme/laptop'
        elif device_type == "desktop":
            return 'atlas://data/images/defaulttheme/desktop'
        else:
            return 'atlas://data/images/defaulttheme/device'

    def update_expiration_timer(self, label, block):
        if block.expiration_time <= time.time():
            # Remove the message
            self.parent.remove_widget(self)
        else:
            remaining = int(block.expiration_time - time.time())
            label.text = f"Disappears in {remaining}s"
            Clock.schedule_once(lambda dt: self.update_expiration_timer(label, block), 1)


class ConnectedDeviceItem(BoxLayout):
    def __init__(self, device_name, device_address, device_type=None, is_favorite=False, **kwargs):
        super(ConnectedDeviceItem, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(10), dp(5)]
        self.device_address = device_address
        self.is_favorite = is_favorite

        # Device icon
        device_icon = Image(
            source=self.get_device_icon(device_type),
            size_hint=(None, 1),
            width=dp(40),
            mipmap=True
        )

        # Device info
        info_layout = BoxLayout(orientation='vertical', padding=[dp(10), 0])
        name_label = AnimatedLabel(
            text=device_name,
            size_hint_y=None,
            height=dp(20),
            bold=True
        )

        addr_label = AnimatedLabel(
            text=f"{device_address[:8]}... | {device_type}",
            size_hint_y=None,
            height=dp(15),
            font_size=dp(10),
            color=LIGHT_TEXT_COLOR
        )

        info_layout.add_widget(name_label)
        info_layout.add_widget(addr_label)

        # Status and favorite buttons
        button_layout = BoxLayout(orientation='vertical', size_hint=(None, 1), width=dp(40))

        status = Image(
            source='atlas://data/images/defaulttheme/checkbox_on',
            size_hint=(None, 1),
            width=dp(20)
        )

        favorite_btn = ToggleButton(
            background_down='atlas://data/images/defaulttheme/star_on',
            background_normal='atlas://data/images/defaulttheme/star_off',
            border=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=dp(20),
            state='down' if is_favorite else 'normal'
        )
        favorite_btn.bind(on_press=self.toggle_favorite)

        button_layout.add_widget(status)
        button_layout.add_widget(favorite_btn)

        self.add_widget(device_icon)
        self.add_widget(info_layout)
        self.add_widget(button_layout)

    def get_device_icon(self, device_type):
        # Return appropriate icon based on device type
        if device_type == "phone":
            return 'atlas://data/images/defaulttheme/phone'
        elif device_type == "tablet":
            return 'atlas://data/images/defaulttheme/tablet'
        elif device_type == "laptop":
            return 'atlas://data/images/defaulttheme/laptop'
        elif device_type == "desktop":
            return 'atlas://data/images/defaulttheme/desktop'
        else:
            return 'atlas://data/images/defaulttheme/device'

    def toggle_favorite(self, instance):
        self.is_favorite = not self.is_favorite
        # This will be handled by the parent app


class GroupItem(BoxLayout):
    def __init__(self, group_name, member_count, **kwargs):
        super(GroupItem, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]

        # Group icon
        group_icon = Image(
            source='atlas://data/images/defaulttheme/group',
            size_hint=(None, 1),
            width=dp(40),
            mipmap=True
        )

        # Group info
        info_layout = BoxLayout(orientation='vertical', padding=[dp(10), 0])
        name_label = AnimatedLabel(
            text=group_name,
            size_hint_y=None,
            height=dp(25),
            bold=True
        )

        member_label = AnimatedLabel(
            text=f"{member_count} members",
            size_hint_y=None,
            height=dp(20),
            font_size=dp(12),
            color=LIGHT_TEXT_COLOR
        )

        info_layout.add_widget(name_label)
        info_layout.add_widget(member_label)

        # Join button
        join_btn = AnimatedButton(
            text="Join",
            size_hint=(None, 1),
            width=dp(80)
        )

        self.add_widget(group_icon)
        self.add_widget(info_layout)
        self.add_widget(join_btn)


class BLENode:
    def __init__(self):
        self.blockchain = Blockchain()
        self.connected_devices: Dict[str, BleakClient] = {}
        self.message_callback = None
        self.device_list_callback = None
        self.running = True
        self.loop = None
        self.thread = None
        self.device_name = "BlockchainChat"
        self.is_server = False  # Flag to indicate if this device is acting as server
        self.device_id = str(uuid.uuid4())  # Unique device ID
        self.crypto_manager = CryptoManager()
        self.groups = {}  # group_id: group_info
        self.store = JsonStore('blockchain_chat.json')  # Local storage

        # Load saved data
        self._load_data()

    def _load_data(self):
        """Load saved data from local storage"""
        try:
            if 'contacts' in self.store:
                for contact_id, public_key_pem in self.store['contacts'].items():
                    self.crypto_manager.add_contact(contact_id, public_key_pem)

            if 'groups' in self.store:
                self.groups = self.store['groups']
        except Exception as e:
            Logger.error(f"Error loading data: {e}")

    def _save_data(self):
        """Save data to local storage"""
        try:
            self.store['contacts'] = {contact_id: self.crypto_manager.get_public_key_pem()
                                      for contact_id in self.crypto_manager.contacts}
            self.store['groups'] = self.groups
        except Exception as e:
            Logger.error(f"Error saving data: {e}")

    def start(self):
        """Start the BLE node in a separate thread"""
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

    def _run_async_loop(self):
        """Run the asyncio event loop in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def validate_block(self, block: Block) -> bool:
        """Validate a block before adding to blockchain"""
        if block.index != self.blockchain.get_latest_block().index + 1:
            return False
        if block.previous_hash != self.blockchain.get_latest_block().hash:
            return False
        if block.hash != block.calculate_hash():
            return False
        return True

    def send_message(self, message: str, recipient_id: str = None, message_type: str = "text",
                     file_data: str = None, file_name: str = None, expiration_seconds: int = None):
        """Send a message to all connected devices or specific recipient"""
        expiration_time = None
        if expiration_seconds:
            expiration_time = time.time() + expiration_seconds

        new_block = Block(
            self.blockchain.get_latest_block().index + 1,
            self.blockchain.get_latest_block().hash,
            datetime.now().timestamp(),
            message,
            sender_id=self.device_id,
            recipient_id=recipient_id,
            message_type=message_type,
            file_data=file_data,
            file_name=file_name,
            expiration_time=expiration_time
        )

        # Encrypt message if recipient is specified
        if recipient_id and recipient_id in self.crypto_manager.contacts:
            try:
                encrypted_message, encryption_key = self.crypto_manager.encrypt_message(message, recipient_id)
                new_block.data = encrypted_message
                new_block.encryption_key = encryption_key
            except Exception as e:
                Logger.error(f"Encryption failed: {e}")
                # Send unencrypted if encryption fails
                new_block.encryption_key = None

        mined_block = self.blockchain.proof_of_work(new_block)
        self.blockchain.add_block(mined_block)

        if self.message_callback:
            self.message_callback(mined_block)

        self.broadcast_block(mined_block)

    def broadcast_block(self, block: Block):
        """Broadcast a block to all connected devices"""
        if not self.loop:
            return

        block_json = block.to_json()

        # Schedule the broadcast in the asyncio loop
        asyncio.run_coroutine_threadsafe(self._broadcast_data(block_json), self.loop)

    async def _broadcast_data(self, data: str):
        """Broadcast data to all connected devices"""
        for address, client in self.connected_devices.items():
            try:
                # Write to the RX characteristic of the connected device
                await client.write_gatt_char(RX_CHAR_UUID, data.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting to client {address}: {e}")

    async def scan_devices(self) -> List[dict]:
        """Scan for nearby BLE devices"""
        devices = []
        try:
            scanned_devices = await BleakScanner.discover()
            for device in scanned_devices:
                if device.name and device.name.startswith(self.device_name):
                    devices.append({
                        "name": device.name,
                        "address": device.address
                    })
        except Exception as e:
            print(f"Error scanning devices: {e}")
        return devices

    async def connect_to_device(self, address: str):
        """Connect to a BLE device"""
        try:
            client = BleakClient(address)
            await client.connect()

            # Store the client
            self.connected_devices[address] = client

            # Update device list
            if self.device_list_callback:
                self.device_list_callback()

            # Exchange public keys
            await client.write_gatt_char(
                RX_CHAR_UUID,
                json.dumps({
                    "type": "key_exchange",
                    "device_id": self.device_id,
                    "public_key": self.crypto_manager.get_public_key_pem()
                }).encode('utf-8')
            )

            # Subscribe to notifications
            def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
                try:
                    data_str = data.decode('utf-8')

                    # Check if it's a key exchange
                    try:
                        msg_data = json.loads(data_str)
                        if msg_data.get("type") == "key_exchange":
                            # Add contact
                            self.crypto_manager.add_contact(
                                msg_data["device_id"],
                                msg_data["public_key"]
                            )
                            self._save_data()
                            return
                    except json.JSONDecodeError:
                        pass

                    # Regular message
                    block = Block.from_json(data_str)

                    # Decrypt if encrypted
                    if block.encryption_key and block.sender_id in self.crypto_manager.contacts:
                        try:
                            block.data = self.crypto_manager.decrypt_message(
                                block.data,
                                block.encryption_key
                            )
                        except Exception as e:
                            Logger.error(f"Decryption failed: {e}")

                    if self.validate_block(block):
                        self.blockchain.add_block(block)
                        if self.message_callback:
                            self.message_callback(block)

                        # Check for pending messages for this sender
                        pending = self.blockchain.get_pending_blocks_for_recipient(block.sender_id)
                        if pending:
                            for pending_block in pending:
                                asyncio.run_coroutine_threadsafe(
                                    self._send_block_to_client(client, pending_block),
                                    self.loop
                                )
                            self.blockchain.remove_pending_blocks(pending)
                except Exception as e:
                    print(f"Error processing notification: {e}")

            # Subscribe to the TX characteristic
            await client.start_notify(TX_CHAR_UUID, notification_handler)

            # Send our latest block to the new device
            latest_block = self.blockchain.get_latest_block()
            block_json = latest_block.to_json()
            await client.write_gatt_char(RX_CHAR_UUID, block_json.encode('utf-8'))

            return True
        except Exception as e:
            print(f"Error connecting to device {address}: {e}")
            return False

    async def _send_block_to_client(self, client, block):
        """Helper method to send a block to a client"""
        try:
            await client.write_gatt_char(
                RX_CHAR_UUID,
                block.to_json().encode('utf-8')
            )
        except Exception as e:
            print(f"Error sending block to client: {e}")

    def stop(self):
        """Stop the BLE node"""
        self.running = False
        if self.loop and self.thread:
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=2)

    async def _stop_server(self):
        """Stop the BLE server"""
        # Disconnect all clients
        for address, client in self.connected_devices.items():
            try:
                await client.disconnect()
            except:
                pass
        self.connected_devices.clear()


class OnboardingScreen(Screen):
    def __init__(self, **kwargs):
        super(OnboardingScreen, self).__init__(**kwargs)
        self.name = 'onboarding'

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # Title
        title = Label(
            text="Welcome to Blockchain Chat",
            font_size=dp(24),
            bold=True,
            color=PRIMARY_COLOR,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)

        # Carousel for onboarding slides
        carousel = Carousel(size_hint=(1, 0.7))

        # Slide 1: Introduction
        slide1 = BoxLayout(orientation='vertical', padding=dp(20))
        slide1.add_widget(Label(
            text="Decentralized messaging powered by blockchain and Bluetooth",
            font_size=dp(18),
            halign='center',
            color=TEXT_COLOR
        ))
        slide1.add_widget(Image(source='atlas://data/images/defaulttheme/logo', size_hint=(0.5, 0.5)))
        carousel.add_widget(slide1)

        # Slide 2: Features
        slide2 = BoxLayout(orientation='vertical', padding=dp(20))
        features = [
            "• End-to-end encryption",
            "• No internet required",
            "• Disappearing messages",
            "• File sharing",
            "• Group messaging"
        ]
        for feature in features:
            slide2.add_widget(Label(text=feature, color=TEXT_COLOR, halign='left'))
        carousel.add_widget(slide2)

        # Slide 3: Permissions
        slide3 = BoxLayout(orientation='vertical', padding=dp(20))
        slide3.add_widget(Label(
            text="This app needs Bluetooth permissions to work",
            font_size=dp(16),
            halign='center',
            color=TEXT_COLOR
        ))
        slide3.add_widget(Image(source='atlas://data/images/defaulttheme/bluetooth', size_hint=(0.3, 0.3)))
        carousel.add_widget(slide3)

        layout.add_widget(carousel)

        # Buttons
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        skip_btn = Button(
            text="Skip",
            background_color=(0.9, 0.9, 0.9, 1),
            color=TEXT_COLOR
        )
        skip_btn.bind(on_press=self.skip_onboarding)

        next_btn = AnimatedButton(text="Next")
        next_btn.bind(on_press=lambda x: carousel.load_next())

        buttons.add_widget(skip_btn)
        buttons.add_widget(next_btn)
        layout.add_widget(buttons)

        self.add_widget(layout)

    def skip_onboarding(self, instance):
        self.manager.current = 'main'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.name = 'main'
        self.node = kwargs.get('node')

        # Main layout
        self.main_layout = BoxLayout(orientation='vertical')

        # Header with app name and status
        self.header = BoxLayout(size_hint=(1, 0.1), padding=[dp(10), dp(5)])
        with self.header.canvas.before:
            Color(PRIMARY_COLOR[0], PRIMARY_COLOR[1], PRIMARY_COLOR[2], 1)
            self.header_rect = Rectangle(pos=self.header.pos, size=self.header.size)
        self.header.bind(pos=self.update_header_rect, size=self.update_header_rect)

        self.title_label = Label(
            text="Blockchain Chat",
            color=(1, 1, 1, 1),
            bold=True,
            size_hint=(0.7, 1)
        )

        self.status_label = Label(
            text="Offline",
            color=(1, 1, 1, 1),
            size_hint=(0.3, 1),
            halign='right'
        )

        self.header.add_widget(self.title_label)
        self.header.add_widget(self.status_label)
        self.main_layout.add_widget(self.header)

        # Tabbed Panel
        self.tabbed_panel = TabbedPanel(
            tab_pos='top_left',
            tab_height=dp(50),
            do_default_tab=False,
            background_color=BACKGROUND_COLOR
        )

        # Chats Tab
        self.chats_tab = TabbedPanelItem(
            text="Chats",
            background_down=SECONDARY_COLOR,
            background_normal=(0.9, 0.9, 0.9, 1)
        )
        self.chats_tab_content = BoxLayout(orientation='vertical')

        # Chat display
        self.chat_scroll = ScrollView(size_hint=(1, 0.6), effect_cls=ScrollEffect)
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=[dp(10), dp(5)])
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        self.chats_tab_content.add_widget(self.chat_scroll)

        # Connected devices section
        self.devices_section = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        self.devices_header = BoxLayout(size_hint=(1, 0.3), padding=[dp(10), 0])
        self.devices_title = AnimatedLabel(
            text="Connected Devices",
            bold=True,
            size_hint=(0.7, 1)
        )

        self.scan_button = AnimatedButton(
            text="Scan",
            size_hint=(0.3, 1)
        )
        self.scan_button.bind(on_press=self.scan_devices)

        self.devices_header.add_widget(self.devices_title)
        self.devices_header.add_widget(self.scan_button)
        self.devices_section.add_widget(self.devices_header)

        self.devices_scroll = ScrollView(size_hint=(1, 0.7))
        self.devices_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=[dp(10), 0])
        self.devices_layout.bind(minimum_height=self.devices_layout.setter('height'))
        self.devices_scroll.add_widget(self.devices_layout)
        self.devices_section.add_widget(self.devices_scroll)

        self.chats_tab_content.add_widget(self.devices_section)

        # Message input
        self.input_layout = BoxLayout(size_hint=(1, 0.15), padding=[dp(10), dp(5)], spacing=dp(10))

        # Attach file button
        self.attach_btn = Button(
            text="📎",
            font_size=dp(20),
            size_hint=(None, 1),
            width=dp(50),
            background_color=(0.9, 0.9, 0.9, 1)
        )
        self.attach_btn.bind(on_press=self.attach_file)

        self.message_input = TextInput(
            multiline=False,
            size_hint=(0.7, 1),
            background_color=(1, 1, 1, 1),
            foreground_color=TEXT_COLOR,
            hint_text="Type a message...",
            hint_text_color=LIGHT_TEXT_COLOR,
            padding=[dp(10), dp(10)]
        )

        self.send_button = AnimatedButton(
            text="Send",
            size_hint=(0.2, 1)
        )
        self.send_button.bind(on_press=self.send_message)

        self.input_layout.add_widget(self.attach_btn)
        self.input_layout.add_widget(self.message_input)
        self.input_layout.add_widget(self.send_button)
        self.chats_tab_content.add_widget(self.input_layout)

        self.chats_tab.add_widget(self.chats_tab_content)
        self.tabbed_panel.add_widget(self.chats_tab)

        # Groups Tab
        self.groups_tab = TabbedPanelItem(
            text="Groups",
            background_down=SECONDARY_COLOR,
            background_normal=(0.9, 0.9, 0.9, 1)
        )
        self.groups_tab_content = BoxLayout(orientation='vertical', padding=[dp(10), dp(10)])

        # Groups list
        self.groups_scroll = ScrollView(size_hint=(1, 0.8))
        self.groups_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.groups_layout.bind(minimum_height=self.groups_layout.setter('height'))
        self.groups_scroll.add_widget(self.groups_layout)
        self.groups_tab_content.add_widget(self.groups_scroll)

        # Create group button
        self.create_group_btn = AnimatedButton(
            text="Create New Group",
            size_hint=(1, None),
            height=dp(50)
        )
        self.create_group_btn.bind(on_press=self.create_group)
        self.groups_tab_content.add_widget(self.create_group_btn)

        self.groups_tab.add_widget(self.groups_tab_content)
        self.tabbed_panel.add_widget(self.groups_tab)

        # Favorites Tab
        self.favorites_tab = TabbedPanelItem(
            text="Favorites",
            background_down=SECONDARY_COLOR,
            background_normal=(0.9, 0.9, 0.9, 1)
        )
        self.favorites_tab_content = BoxLayout(orientation='vertical', padding=[dp(10), dp(10)])

        # Favorites list
        self.favorites_scroll = ScrollView(size_hint=(1, 1))
        self.favorites_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.favorites_layout.bind(minimum_height=self.favorites_layout.setter('height'))
        self.favorites_scroll.add_widget(self.favorites_layout)
        self.favorites_tab_content.add_widget(self.favorites_scroll)

        self.favorites_tab.add_widget(self.favorites_tab_content)
        self.tabbed_panel.add_widget(self.favorites_tab)

        # Settings Tab
        self.settings_tab = TabbedPanelItem(
            text="Settings",
            background_down=SECONDARY_COLOR,
            background_normal=(0.9, 0.9, 0.9, 1)
        )
        self.settings_tab_content = BoxLayout(orientation='vertical', padding=[dp(20), dp(20)])

        # Profile section
        profile_layout = BoxLayout(size_hint_y=None, height=dp(100), spacing=dp(20))

        # Avatar placeholder
        avatar = Image(
            source='atlas://data/images/defaulttheme/user',
            size_hint=(None, 1),
            width=dp(80)
        )

        # User info
        user_info = BoxLayout(orientation='vertical')
        user_id_label = AnimatedLabel(
            text=f"ID: {self.node.device_id[:8]}...",
            bold=True
        )
        device_type = self.get_device_type()
        device_label = AnimatedLabel(
            text=f"Device: {device_type}",
            color=LIGHT_TEXT_COLOR
        )

        user_info.add_widget(user_id_label)
        user_info.add_widget(device_label)

        profile_layout.add_widget(avatar)
        profile_layout.add_widget(user_info)
        self.settings_tab_content.add_widget(profile_layout)

        # Settings options
        settings_options = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None, height=dp(300))

        # Disappearing messages
        disappear_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        disappear_label = AnimatedLabel(text="Disappearing Messages")
        disappear_switch = Switch(size_hint=(None, 1), width=dp(50))
        disappear_layout.add_widget(disappear_label)
        disappear_layout.add_widget(disappear_switch)
        settings_options.add_widget(disappear_layout)

        # Dark mode
        dark_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        dark_label = AnimatedLabel(text="Dark Mode")
        dark_switch = Switch(size_hint=(None, 1), width=dp(50))
        dark_layout.add_widget(dark_label)
        dark_layout.add_widget(dark_switch)
        settings_options.add_widget(dark_layout)

        # Encryption
        encrypt_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        encrypt_label = AnimatedLabel(text="End-to-End Encryption")
        encrypt_switch = Switch(active=True, size_hint=(None, 1), width=dp(50))
        encrypt_layout.add_widget(encrypt_label)
        encrypt_layout.add_widget(encrypt_switch)
        settings_options.add_widget(encrypt_layout)

        # QR Code for pairing
        qr_btn = AnimatedButton(
            text="Show QR Code for Pairing",
            size_hint=(1, None),
            height=dp(50)
        )
        qr_btn.bind(on_press=self.show_qr_code)
        settings_options.add_widget(qr_btn)

        self.settings_tab_content.add_widget(settings_options)

        # Logout button
        logout_btn = AnimatedButton(
            text="Logout",
            size_hint=(1, None),
            height=dp(50),
            background_color=ACCENT_COLOR
        )
        logout_btn.bind(on_press=self.logout)
        self.settings_tab_content.add_widget(logout_btn)

        self.settings_tab.add_widget(self.settings_tab_content)
        self.tabbed_panel.add_widget(self.settings_tab)

        self.main_layout.add_widget(self.tabbed_panel)

        # Initialize groups display
        self.update_groups_display()

        Clock.schedule_interval(self.update_device_list, 5)
        self.add_widget(self.main_layout)

    def update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def send_message(self, instance):
        message = self.message_input.text.strip()
        if message:
            # Check if disappearing messages is enabled
            expiration_seconds = None
            # In a real app, this would be based on user settings

            self.node.send_message(message, expiration_seconds=expiration_seconds)
            self.message_input.text = ""

    def update_chat(self, block):
        # Animate existing messages up
        for child in self.chat_layout.children:
            anim = Animation(y=child.y + dp(60), duration=0.3)
            anim.start(child)

        # Add new message
        is_self = block.sender_id == self.node.device_id
        device_type = self.get_device_type() if not is_self else None
        bubble = MessageBubble(block, is_self=is_self, device_type=device_type)
        self.chat_layout.add_widget(bubble)

        # Scroll to bottom
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(bubble), 0.1)

        # Mark as read if it's from someone else
        if not is_self:
            block.status = "read"
            # In a real app, we would send a read receipt

    def scan_devices(self, instance):
        if not self.node.loop:
            return

        # Schedule the scan in the asyncio loop
        asyncio.run_coroutine_threadsafe(self._scan_and_show_devices(), self.node.loop)

    async def _scan_and_show_devices(self):
        devices = await self.node.scan_devices()

        def show_devices():
            device_popup = BoxLayout(orientation='vertical', padding=[dp(20), dp(20)])
            device_list = BoxLayout(orientation='vertical', spacing=dp(10))

            for device in devices:
                device_type = self.infer_device_type(device['name'])
                btn = AnimatedButton(
                    text=f"{device['name']}\n{device_type}",
                    size_hint_y=None,
                    height=dp(60),
                    halign='left',
                    valign='middle'
                )
                btn.bind(on_press=lambda btn, addr=device['address']: self.connect_to_device(addr, device_type))
                device_list.add_widget(btn)

            if not devices:
                device_list.add_widget(Label(text="No devices found", color=TEXT_COLOR))

            device_popup.add_widget(device_list)
            close_btn = AnimatedButton(
                text="Close",
                size_hint_y=None,
                height=dp(50),
                background_color=ACCENT_COLOR
            )
            close_btn.bind(on_press=lambda btn: popup.dismiss())
            device_popup.add_widget(close_btn)

            popup = Popup(
                title="Available Devices",
                content=device_popup,
                size_hint=(0.9, 0.9),
                title_color=PRIMARY_COLOR,
                title_size=dp(20),
                separator_color=PRIMARY_COLOR
            )
            popup.open()

        # Run in main thread
        Clock.schedule_once(lambda dt: show_devices(), 0)

    def connect_to_device(self, address, device_type):
        if not self.node.loop:
            return

        # Schedule the connection in the asyncio loop
        asyncio.run_coroutine_threadsafe(self._connect_and_update(address, device_type), self.node.loop)

    async def _connect_and_update(self, address, device_type):
        success = await self.node.connect_to_device(address)

        def update_ui():
            if success:
                self.update_chat(Block(
                    index=0,
                    previous_hash="",
                    timestamp=time.time(),
                    data=f"Connected to {address[:8]}...",
                    sender_id=self.node.device_id
                ))
                self.status_label.text = f"Connected ({len(self.node.connected_devices)})"
                # Add to favorites by default
                self.node.favorites[address] = {
                    "name": f"Device {address[:8]}...",
                    "type": device_type,
                    "is_favorite": True
                }
                self.update_favorites_display()
            else:
                self.update_chat(Block(
                    index=0,
                    previous_hash="",
                    timestamp=time.time(),
                    data=f"Failed to connect to {address[:8]}...",
                    sender_id=self.node.device_id
                ))

        # Run in main thread
        Clock.schedule_once(lambda dt: update_ui(), 0)

    def update_device_list(self, dt):
        # Update connected devices display if needed
        pass

    def update_connected_devices(self):
        # Clear the current list
        self.devices_layout.clear_widgets()

        # Add each connected device
        for address, client in self.node.connected_devices.items():
            device_type = self.infer_device_type(f"Device {address[:8]}...")
            is_favorite = address in self.node.favorites and self.node.favorites[address]["is_favorite"]

            device_item = ConnectedDeviceItem(
                device_name=f"Device {address[:8]}...",
                device_address=address,
                device_type=device_type,
                is_favorite=is_favorite
            )
            device_item.favorite_btn.bind(on_press=lambda btn, addr=address: self.toggle_favorite(addr))
            self.devices_layout.add_widget(device_item)

        # Update status
        self.status_label.text = f"Connected ({len(self.node.connected_devices)})"

    def toggle_favorite(self, address):
        if address in self.node.favorites:
            self.node.favorites[address]["is_favorite"] = not self.node.favorites[address]["is_favorite"]
            self.update_connected_devices()
            self.update_favorites_display()

    def update_favorites_display(self):
        self.favorites_layout.clear_widgets()

        for address, info in self.node.favorites.items():
            if info["is_favorite"]:
                device_item = ConnectedDeviceItem(
                    device_name=info["name"],
                    device_address=address,
                    device_type=info["type"],
                    is_favorite=True
                )
                device_item.favorite_btn.bind(on_press=lambda btn, addr=address: self.toggle_favorite(addr))
                self.favorites_layout.add_widget(device_item)

    def update_groups_display(self):
        self.groups_layout.clear_widgets()

        for group_name, group_info in self.node.groups.items():
            group_item = GroupItem(
                group_name=group_name,
                member_count=group_info["members"]
            )
            self.groups_layout.add_widget(group_item)

    def create_group(self, instance):
        # Placeholder for group creation
        self.update_chat(Block(
            index=0,
            previous_hash="",
            timestamp=time.time(),
            data="Group creation feature coming soon!",
            sender_id=self.node.device_id
        ))

    def attach_file(self, instance):
        # Placeholder for file attachment
        self.update_chat(Block(
            index=0,
            previous_hash="",
            timestamp=time.time(),
            data="File attachment feature coming soon!",
            sender_id=self.node.device_id
        ))

    def show_qr_code(self, instance):
        # Generate QR code with device ID and public key
        qr_data = json.dumps({
            "device_id": self.node.device_id,
            "public_key": self.node.crypto_manager.get_public_key_pem()
        })

        qr_img = qrcode.make(qr_data)

        # Convert to Kivy compatible format
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        img_data = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Show QR code popup
        qr_popup = BoxLayout(orientation='vertical', padding=dp(20))
        qr_img_widget = Image(source=f"data:image/png;base64,{img_data}", size_hint=(1, 0.8))
        qr_popup.add_widget(qr_img_widget)

        close_btn = AnimatedButton(
            text="Close",
            size_hint=(1, None),
            height=dp(50)
        )
        close_btn.bind(on_press=lambda btn: popup.dismiss())
        qr_popup.add_widget(close_btn)

        popup = Popup(
            title="Your QR Code",
            content=qr_popup,
            size_hint=(0.8, 0.8),
            title_color=PRIMARY_COLOR
        )
        popup.open()

    def logout(self, instance):
        # Reset app state
        self.node.stop()
        self.manager.current = 'onboarding'

    def infer_device_type(self, device_name):
        # Simple heuristic to infer device type from name
        device_name_lower = device_name.lower()

        if "phone" in device_name_lower or "mobile" in device_name_lower:
            return "phone"
        elif "tablet" in device_name_lower:
            return "tablet"
        elif "laptop" in device_name_lower or "notebook" in device_name_lower:
            return "laptop"
        elif "desktop" in device_name_lower or "pc" in device_name_lower:
            return "desktop"
        else:
            # Default based on platform
            if platform == "android":
                return "phone"
            elif platform == "ios":
                return "phone" if "ipad" not in device_name_lower else "tablet"
            elif platform == "win":
                return "laptop"
            elif platform == "linux":
                return "desktop"
            elif platform == "macosx":
                return "laptop"
            else:
                return "device"

    def get_device_type(self):
        # Get device type for current device
        if platform == "android":
            return "phone"
        elif platform == "ios":
            return "phone"  # Could check for iPad but this is a simple implementation
        elif platform == "win":
            return "laptop"
        elif platform == "linux":
            return "desktop"
        elif platform == "macosx":
            return "laptop"
        else:
            return "device"


class BlockchainChatApp(App):
    def build(self):
        Window.clearcolor = BACKGROUND_COLOR

        # Create BLE node
        self.node = BLENode()
        self.node.message_callback = self.update_chat
        self.node.device_list_callback = self.update_connected_devices
        self.node.start()

        # Initialize favorites and groups
        self.node.favorites = {}  # device_address: device_info
        self.node.groups = {
            "Developers": {"members": 5, "icon": "atlas://data/images/defaulttheme/group"},
            "Friends": {"members": 3, "icon": "atlas://data/images/defaulttheme/group"},
            "Family": {"members": 4, "icon": "atlas://data/images/defaulttheme/group"}
        }

        # Create screen manager
        self.sm = ScreenManager(transition=FadeTransition())

        # Add screens
        self.sm.add_widget(OnboardingScreen())
        self.sm.add_widget(MainScreen(node=self.node))

        return self.sm

    def update_chat(self, block):
        # Find the main screen and update chat
        main_screen = self.sm.get_screen('main')
        main_screen.update_chat(block)

    def update_connected_devices(self):
        # Find the main screen and update connected devices
        main_screen = self.sm.get_screen('main')
        main_screen.update_connected_devices()

    def on_stop(self):
        self.node.stop()


if __name__ == '__main__':
    BlockchainChatApp().run()