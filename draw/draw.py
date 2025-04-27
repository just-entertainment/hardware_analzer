# er_diagram_generator.py
import os


def generate_er_diagram():
    """生成符合DOT语法的CPU ER图"""
    dot_content = """digraph CPU_ER_Diagram {
    rankdir=LR;
    node [shape=none, margin=0];

    /* CPU实体 */
    CPU [label=<
        <table border="0" cellborder="1" cellspacing="0">
            <tr><td colspan="2" bgcolor="#d6d6d6"><b>CPU</b></td></tr>
            <tr><td align="left" port="pk">PK</td><td align="left">product_id</td></tr>
            <tr><td colspan="2"><hr/></td></tr>
            <tr><td align="left" colspan="2">title</td></tr>
            <tr><td align="left" colspan="2">reference_price</td></tr>
            <tr><td align="left" colspan="2">jd_price</td></tr>
            <tr><td align="left" colspan="2">product_image</td></tr>
            <tr><td colspan="2"><hr/></td></tr>
            <tr><td align="left" colspan="2">suitable_type</td></tr>
            <tr><td align="left" colspan="2">cpu_series</td></tr>
            <tr><td align="left" colspan="2">cpu_frequency</td></tr>
        </table>
    >];

    /* CPUPriceHistory实体 */
    CPUPriceHistory [label=<
        <table border="0" cellborder="1" cellspacing="0">
            <tr><td colspan="2" bgcolor="#d6d6d6"><b>CPUPriceHistory</b></td></tr>
            <tr><td align="left">PK</td><td align="left">id</td></tr>
            <tr><td align="left" port="fk">FK</td><td align="left">cpu_id</td></tr>
            <tr><td colspan="2"><hr/></td></tr>
            <tr><td align="left" colspan="2">price</td></tr>
            <tr><td align="left" colspan="2">date</td></tr>
            <tr><td align="left" colspan="2">created_at</td></tr>
        </table>
    >];

    /* 关系定义 */
    CPU:pk -> CPUPriceHistory:fk [
        label="1:N",
        dir=both,
        arrowtail=crow,
        arrowhead=none
    ];
}"""

    # 写入文件
    with open("cpu_er.dot", "w", encoding="utf-8") as f:
        f.write(dot_content)

    print(f"DOT文件已生成: {os.path.abspath('cpu_er.dot')}")
    print("请将文件内容复制到以下在线工具查看:")
    print("1. https://edotor.net/")
    print("2. https://dreampuf.github.io/GraphvizOnline/")


if __name__ == "__main__":
    generate_er_diagram()
