import re
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

def read_chat_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def parse_message(line):
    # Pattern for WhatsApp messages: [date, time] sender: message
    pattern = r'\[(.*?)\] (.*?): (.*)'
    match = re.match(pattern, line)
    
    if match:
        datetime_str, sender, message = match.groups()
        try:
            # Parse datetime
            timestamp = datetime.strptime(datetime_str, '%d/%m/%Y, %H:%M:%S')
            return {
                'timestamp': timestamp,
                'sender': sender.strip(),
                'message': message.strip()
            }
        except ValueError:
            return None
    return None

def analyze_chat(messages):
    # Initialize counters
    message_counts = Counter()
    hour_activity = Counter()
    message_lengths = {}
    
    for msg in messages:
        if msg:
            # Count messages per sender
            message_counts[msg['sender']] += 1
            
            # Track hour activity
            hour_activity[msg['timestamp'].hour] += 1
            
            # Track message lengths
            if msg['sender'] not in message_lengths:
                message_lengths[msg['sender']] = []
            message_lengths[msg['sender']].append(len(msg['message']))
    
    return message_counts, hour_activity, message_lengths

def print_stats(message_counts, hour_activity, message_lengths, chat_name):
    print(f"\n=== WhatsApp Chat Analysis for {chat_name} ===\n")
    
    print("Messages per person:")
    total_messages = sum(message_counts.values())
    for person, count in message_counts.most_common():
        percentage = (count / total_messages) * 100
        print(f"{person}: {count} messages ({percentage:.1f}%)")
    
    print("\nMost active hours:")
    for hour, count in sorted(hour_activity.most_common()[:5]):
        print(f"{hour:02d}:00 - {hour:02d}:59: {count} messages")
    
    print("\nAverage message length per person:")
    for person, lengths in message_lengths.items():
        avg_length = sum(lengths) / len(lengths)
        print(f"{person}: {avg_length:.1f} characters")
    
    print(f"\nTotal messages: {total_messages}")

def process_chat_file(file_path):
    try:
        # Read and parse chat
        chat_lines = read_chat_file(file_path)
        messages = [parse_message(line) for line in chat_lines if line.strip()]
        messages = [msg for msg in messages if msg is not None]
        
        if not messages:
            print(f"No valid messages found in {file_path}")
            return
        
        # Analyze and print stats
        message_counts, hour_activity, message_lengths = analyze_chat(messages)
        print_stats(message_counts, hour_activity, message_lengths, file_path.name)
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    # Create chats directory if it doesn't exist
    chats_dir = Path('chats')
    chats_dir.mkdir(exist_ok=True)
    
    # Process all .txt files in the chats directory
    chat_files = list(chats_dir.glob('*.txt'))
    
    if not chat_files:
        print("No chat files found in the 'chats' directory!")
        return
    
    print(f"Found {len(chat_files)} chat file(s)")
    
    for chat_file in chat_files:
        print(f"\nProcessing: {chat_file}")
        process_chat_file(chat_file)

if __name__ == "__main__":
    main()
