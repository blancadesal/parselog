import csv
from datetime import datetime
import click

# Function to parse the timestamp from a log entry
def parse_timestamp(log_entry):
    parts = log_entry.split()
    for part in parts:
        if part.endswith('Z'):
            timestamp_str = part.rstrip('Z')
            return datetime.fromisoformat(timestamp_str)
    raise ValueError(f"No valid timestamp found in log entry: {log_entry}")

# Function to extract the step name and the log message
def extract_step_and_message(log_entry):
    parts = log_entry.split(' ', 3)
    if len(parts) < 2:
        raise ValueError(f"Log entry format is incorrect: {log_entry}")
    step_name = parts[0].strip('[]')
    message = parts[3] if len(parts) == 4 else ""
    # Remove the redundant timestamp from the message, strip newlines and replace internal newlines
    message_parts = message.split(' ', 2)
    if len(message_parts) >= 3:
        message = ' '.join(message_parts[2:]).strip()
    message = message.replace('\n', ' ').replace('\r', '')
    return step_name, message


# CLI command definition
@click.command()
@click.option('-f', '--file', 'input_file', required=True, type=click.File('r'), help='Input file containing log entries')
@click.option('-o', '--output', 'output_file', required=True, type=str, help='Output CSV file')
def parselog(input_file, output_file):
    log_entries = input_file.readlines()

    # Parse and sort the log entries by timestamp
    sorted_logs = sorted(log_entries, key=parse_timestamp)

    # Write to CSV output
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["id", "step", "timestamp", "entry", "delta"])

        prev_time = parse_timestamp(sorted_logs[0]) if sorted_logs else None
        index = 1  # Initialize the index counter
        for log in sorted_logs:
            try:
                current_time = parse_timestamp(log)
                step_name, message = extract_step_and_message(log)
                delta = (current_time - prev_time).total_seconds() if prev_time else 0
                formatted_delta = f"{delta:.4f}"
                csv_writer.writerow([index, step_name, current_time.isoformat(), message, formatted_delta])
                prev_time = current_time
                index += 1  # Increment the index for the next entry
            except ValueError as e:
                click.echo(f"Warning: {e}", err=True)

    click.echo(f"Processed log entries written to {output_file}")


if __name__ == '__main__':
    parselog()
