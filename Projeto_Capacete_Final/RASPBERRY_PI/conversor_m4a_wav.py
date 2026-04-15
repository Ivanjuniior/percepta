import os
import subprocess

input_dir = "audios_m4a"
output_dir = "audios_wav"

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    if file.endswith(".m4a"):
        input_path = os.path.join(input_dir, file)

        output_name = os.path.splitext(file)[0] + ".wav"
        output_path = os.path.join(output_dir, output_name)

        print(f"Convertendo: {file} -> {output_name}")

        subprocess.run([
            "ffmpeg",
            "-y",              # sobrescreve se existir
            "-i", input_path,
            "-ac", "1",        # mono (melhor pra robótica)
            "-ar", "16000",    # qualidade leve e eficiente
            output_path
        ])

print("Conversão finalizada!")