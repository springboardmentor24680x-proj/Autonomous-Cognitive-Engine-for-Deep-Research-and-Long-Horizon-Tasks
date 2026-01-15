import re
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.memory.vfs import VFS, read_file


def create_visualization(
    source_file: str,
    chart_type: str,
    title: str = ""
) -> str:
    """
    Create a visualization from a data block stored in a VFS file.
    Supported chart types: bar, horizontal_bar, pie, line, area, scatter
    """

    content = read_file(source_file)
    if isinstance(content, str) and content.startswith("File"):
        return f"Error: {content}"

    # ---- Extract DATA FOR GRAPHING ----
    headers = ["DATA FOR GRAPHING", "DATA BLOCK", "GRAPH DATA"]
    data_text = ""

    for h in headers:
        if h in content:
            data_text = content.split(h, 1)[-1]
            data_text = re.split(r"END DATA|END GRAPH|---|#", data_text)[0].strip()
            break

    if not data_text:
        return "Visualization failed: No valid data block found."

    chart_type = chart_type.lower()
    plt.figure(figsize=(10, 6))

    try:
        # ---------- Scatter ----------
        if chart_type == "scatter":
            x, y = [], []
            for line in data_text.splitlines():
                nums = re.findall(r"\d+(?:\.\d+)?", line)
                if len(nums) >= 2:
                    x.append(float(nums[0]))
                    y.append(float(nums[1]))

            if not x:
                return "Invalid scatter data. Expected numeric X,Y pairs."

            plt.scatter(x, y)
            plt.xlabel("X")
            plt.ylabel("Y")

        # ---------- Bar / Pie ----------
        elif chart_type in {"bar", "horizontal_bar", "pie"}:
            pairs = re.findall(r"([A-Za-z0-9\s]+):\s*(\d+(?:\.\d+)?)", data_text)
            if not pairs:
                return "Invalid categorical data. Expected 'Label: Value'."

            labels = [p[0].strip() for p in pairs]
            values = [float(p[1]) for p in pairs]

            if chart_type == "bar":
                plt.bar(labels, values)
                plt.xticks(rotation=45, ha="right")
            elif chart_type == "horizontal_bar":
                plt.barh(labels, values)
            else:
                plt.pie(values, labels=labels, autopct="%1.1f%%")

        # ---------- Line / Area ----------
        elif chart_type in {"line", "area"}:
            pairs = re.findall(r"(\d+(?:\.\d+)?)\s*[:,]\s*(\d+(?:\.\d+)?)", data_text)
            if not pairs:
                return "Invalid line/area data."

            x = [float(p[0]) for p in pairs]
            y = [float(p[1]) for p in pairs]
            x, y = zip(*sorted(zip(x, y)))

            if chart_type == "line":
                plt.plot(x, y, marker="o")
            else:
                plt.fill_between(x, y, alpha=0.4)
                plt.plot(x, y)

        else:
            return f"Unsupported chart type: {chart_type}"

        plt.title(title or f"{chart_type.title()} Chart")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()

        output_name = source_file.replace(".txt", f"_{chart_type}.png")
        VFS[output_name] = buf.getvalue()

        return f"SUCCESS: Chart saved as {output_name}"

    except Exception as e:
        plt.close()
        return f"Visualization error: {e}"
