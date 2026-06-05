with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

target_idx = -1
for idx, line in enumerate(lines):
    if 'def set_tp_sl(' in line:
        target_idx = idx
        break

if target_idx != -1:
    print(f"Found set_tp_sl at line {target_idx}")
    # find the next except block
    except_idx = -1
    for idx in range(target_idx, target_idx + 100):
        if 'except Exception as exc:' in lines[idx]:
            except_idx = idx
            break
    
    if except_idx != -1:
        print(f"Found except block at line {except_idx}")
        # We will replace lines from except_idx to except_idx + 6
        new_except_lines = [
            '    except Exception as exc:\n',
            '        print("TP/SL error:", exc)\n',
            '        text = str(exc)\n',
            '        if "code=-4006" in text or "Stop price less than zero" in text or "code=-4130" in text or "code=-2021" in text or "immediately trigger" in text:\n',
            '            print(f"TP/SL skipped {symbol}: stop price invalid/duplicate di exchange ({text}), lanjut tanpa TP/SL order.")\n',
            '            return\n',
            '        # Swallow all TP/SL exceptions to guarantee trading flow is never blocked\n',
            '        print(f"TP/SL warning {symbol}: {text}. Swallowed to protect trading loop.")\n',
            '        return\n'
        ]
        
        # Determine how many lines to remove (until the next function def validate_tp_sl)
        end_idx = -1
        for idx in range(except_idx, except_idx + 20):
            if 'def validate_tp_sl' in lines[idx]:
                end_idx = idx
                break
        
        if end_idx != -1:
            print(f"Replacing lines from {except_idx} to {end_idx}")
            lines[except_idx:end_idx] = new_except_lines
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print("Successfully updated app.py!")
        else:
            print("Could not find end of except block")
else:
    print("Could not find set_tp_sl")
