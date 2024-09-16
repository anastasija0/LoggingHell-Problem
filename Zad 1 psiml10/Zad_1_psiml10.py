import os
import re
from datetime import datetime, timedelta
#import numpy as np

#A)
def count_log_files(directory):
    total_log_files = 0
    total_log_lines = 0
    total_error_files = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.logtxt'):
                total_log_files += 1
                file_path = os.path.join(root, file)
                total_log_lines+=count_log_lines(file_path)
                total_error_files+=check_error_line(file_path)
    print(total_log_files)
    print(total_log_lines)
    print(total_error_files)
#B)
def count_log_lines(file):
    total_nonempty_lines = 0
    with open(file, 'r') as f:
                    for line in f:
                        if line.strip():
                            total_nonempty_lines += 1
    return total_nonempty_lines
#C)
def check_error_line(file):
    error = 0
    with open(file, 'r') as f:
      for line in f:
        match_result = check_line_format(line)
        if match_result is not None:
          format = match_result[0]
          match = match_result[1]
          if format == 1:
            service_name = match.group(1)
            log_level= match.group(2)
            message = match.group(3)
            if log_level == "err":
              return 1
          elif format == 2:
            log_level = match.group(1)
            service_name = match.group(2)
            message = match.group(3)
            if log_level == "fatal-error":
              return 1
          elif format == 3:
            log_level = match.group(1)
            service_name= match.group(2)
            message = match.group(3)
            if log_level == "ERROR":
              return 1
          elif format == 4:
            service_name = match.group(1)
            log_level= match.group(2)
            message = match.group(3)
            if log_level == "error":
              return 1
          elif format == 5:
            log_level = match.group(1)
            service_name= match.group(2)
            message = match.group(3)
            if log_level == "error":
              return 1
    return error
def check_line_format(line):
  pattern1 = r'\d{4} \d{2} \d{2} \d{2}:\d{2}:\d{2} (.*?): <(.*?)> (.*?)$'
  pattern2 = r'\d{2}\.\d{2}\.\d{4}\.\d{2}h:\d{2}m:\d{2}s (.*?) (.*?) --- (.*?)$'
  pattern3 = r'dt=\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2} level=(.*?) service=(.*?) msg=(.*?)$'
  pattern4 = r'\d{2}\.\d{2}\.\d{4}\.\d{2}:\d{2}:\d{2} CEF:0\|(.*?)\|loglevel=(.*?) msg=(.*?)$'
  pattern5 = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[(.*?)\] \[(.*?)\] - (.*?)$'
  if re.match(pattern1,line):
    match = re.match(pattern1,line)
    return [1,match]
  elif re.match(pattern2,line):
    match = re.match(pattern2,line)
    return [2,match]
  elif re.match(pattern3,line):
    match = re.match(pattern3,line)
    return [3,match]
  elif re.match(pattern4,line):
    match = re.match(pattern4,line)
    return [4,match]
  elif re.match(pattern5,line):
    match = re.match(pattern5,line)
    return [5,match]

def extract_message_body(line):
  match_result = check_line_format(line)
  if match_result is not None:
    match = match_result[1]
    return match.group(3)
    
#D)
def count_common_words(directory):
    word_counts = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.logtxt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    for line in f:
                        message_body = extract_message_body(line)
                        if message_body is not None:  
                          words = re.findall(r'\b\w+\b', message_body)
                          appears = {}
                          for word in words:
                            if word not in appears:
                              if word in word_counts:
                                word_counts[word] += 1
                                appears[word] = 1
                              else:
                                word_counts[word] = 1
                                appears[word] = 1
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    if len(sorted_word_counts)<5: 
      return sorted_word_counts
    else:
      most_common_words = [word for word, _ in sorted_word_counts[:5]]
      return most_common_words
  #E)
def find_longest_warning_period(directory):
  warning_timestamps = []

  for root, dirs, files in os.walk(directory):
      for file in files:
          if file.endswith('.logtxt'):
              file_path = os.path.join(root, file)
              with open(file_path, 'r') as f:
                  for line in f:
                      timestamp = extract_timestamp(line)
                      if timestamp is not None:
                        if is_warning(line):
                          warning_timestamps.append(timestamp)

  warning_timestamps.sort()
  max_warning_count = 5
  max_duration = timedelta(0)

  warning_length = len(warning_timestamps)
  if (warning_length<=5):
    max_duration = warning_timestamps[-1] - warning_timestamps[0]
  else:
    for i in range (0,warning_length-2):
      current_warning_count = 1
      current_start = warning_timestamps[i]
      current_end = warning_timestamps[i]
      for j in range(i+1,warning_length-1):
        if current_warning_count < max_warning_count:
          current_warning_count+=1;
          current_end = warning_timestamps[j]
        else:
          break
      current_duration = current_end - current_start
      if current_duration > max_duration:
        max_duration = current_duration
  max_duration_seconds = max_duration.total_seconds()
  return int(max_duration_seconds)
def extract_timestamp(line):
  match_result = check_line_format(line)
  if match_result is not None:
    format = match_result[0]
    text = match_result[1]
    ts_pattern1 = r'(\d{4} \d{2} \d{2} \d{2}:\d{2}:\d{2})'
    ts_pattern2 = r'(\d{2}\.\d{2}\.\d{4}\.\d{2}h:\d{2}m:\d{2}s)'
    ts_pattern3 = r'(dt=\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})'
    ts_pattern4 = r'(\d{2}\.\d{2}\.\d{4}\.\d{2}:\d{2}:\d{2})'
    ts_pattern5 = r'(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\])'
    #match = re.search(timestamp_pattern, line)
    if format == 1:
      match = re.search(ts_pattern1, line)
      timestamp_str = match.group(1)
      return datetime.strptime(timestamp_str, '%Y %m %d %H:%M:%S')
    elif format == 2:
      match = re.search(ts_pattern2, line)
      timestamp_str = match.group(1)
      return datetime.strptime(timestamp_str, '%d.%m.%Y.%Hh:%Mm:%Ss')
    elif format == 3:
      match = re.search(ts_pattern3, line)
      timestamp_str = match.group(1)
      return datetime.strptime(timestamp_str, 'dt=%Y-%m-%d_%H:%M:%S')
    elif format == 4:
      match = re.search(ts_pattern4, line)
      timestamp_str = match.group(1)
      return datetime.strptime(timestamp_str, '%d.%m.%Y.%H:%M:%S')
    elif format == 5:
      match = re.search(ts_pattern5, line)
      timestamp_str = match.group(1)
      return datetime.strptime(timestamp_str, '[%Y-%m-%d %H:%M:%S]')
def is_warning(line):
  result= check_line_format(line)
  if result is not None:
    format = result[0]
    match = result[1]
    if (format == 1) & (match.group(2) == "warn"):
      return 1
    elif (format == 2) & (match.group(1) == "the-warning"):
      return 1
    elif (format == 3) & (match.group(1) == "WARN"):
      return 1
    elif (format == 4) & (match.group(2) == "warning"):
      return 1
    elif (format == 5) & (match.group(1) == "warning"):
      return 1
    else: return 0

if __name__ == "__main__":
    #input is path to the directory where set is stored
    directory_path = input()
    #contents = os.listdir(directory_path)
    count_log_files(directory_path)
    most_common_words=count_common_words(directory_path)
    result = ', '.join(most_common_words)
    print(result)
    longest_warning_period = find_longest_warning_period(directory_path)
    print(longest_warning_period)


