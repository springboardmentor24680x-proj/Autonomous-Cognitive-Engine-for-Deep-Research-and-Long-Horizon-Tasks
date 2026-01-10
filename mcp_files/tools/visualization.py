import matplotlib.pyplot as plt
import re
import io
import base64
from tools.vfs import read_file, write_file

def create_visualization(filename: str, output_name: str = "chart.png"):
    """
    Parses 'Brand: Number' from the VFS file and saves a PNG.
    """
    content = read_file(filename)
    
    # Extract data between 'DATA FOR GRAPHING' and the end of the block
    data_match = re.search(r"DATA FOR GRAPHING\n(.*?)(?:\n\n|$)", content, re.DOTALL)
    if not data_match:
        return "Error: No 'DATA FOR GRAPHING' section found in file."

    lines = data_match.group(1).strip().split('\n')
    labels = []
    values = []

    for line in lines:
        if ":" in line:
            brand, count = line.split(":")
            labels.append(brand.strip())
            # Clean numeric strings (remove commas, etc)
            clean_val = re.sub(r'[^\d.]', '', count)
            values.append(float(clean_val))

    if not labels:
        return "Error: No valid data points found."

    # Generate Plot
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.title("Market Research Data")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save to Bytes then to VFS
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Crucial: Save as bytes for the VFS to handle correctly
    write_file(output_name, buf.getvalue())
    
    return f"Successfully created chart: {output_name}"