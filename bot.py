import os
import shutil
import patoolib
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Get these from GitHub Secrets
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handler(event):
    if event.document:
        filename = event.document.attributes[0].file_name if event.document.attributes else "archive"
        
        if filename.lower().endswith(('.zip', '.rar', '.7z', '.tar')):
            status = await event.reply("⚡ **Starting...**\n📥 Downloading archive...")
            
            # 1. Download
            dl_path = await event.download_media()
            
            # 2. Extract
            extract_dir = "unpacked_files"
            if os.path.exists(extract_dir): shutil.rmtree(extract_dir)
            os.makedirs(extract_dir)
            
            try:
                await status.edit("📦 **Extracting...**\nThis might take a moment for large files.")
                patoolib.extract_archive(dl_path, outdir=extract_dir)
                
                # 3. Upload extracted files
                await status.edit("📤 **Uploading extracted files...**")
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_full_path = os.path.join(root, file)
                        await client.send_file(event.chat_id, file_full_path, caption=f"📄 `{file}`")
                
                await status.edit("✅ **Done!** Extraction complete.")
            except Exception as e:
                await event.reply(f"❌ **Error:**\n`{str(e)}`")
            finally:
                # Cleanup to save runner space
                if os.path.exists(dl_path): os.remove(dl_path)
                if os.path.exists(extract_dir): shutil.rmtree(extract_dir)

print("Userbot is live...")
client.start()
client.run_until_disconnected()
