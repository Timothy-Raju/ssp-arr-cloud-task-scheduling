"""
generate_ieee_documents.py
Generates publication-quality IEEE Conference documents matching the official IEEE template:
1. SSP_ARR_Research_Paper.pdf (ReportLab, multi-template IEEE 2-column & full-width tables/figures)
2. SSP_ARR_Research_Paper.docx (python-docx, official IEEE 2-column formatting, author blocks, all tables, equations, embedded figures)
"""
import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted, FrameBreak, PageBreak, NextPageTemplate, KeepTogether, Image as RLImage
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL SHARED DATASETS
# ─────────────────────────────────────────────────────────────────────────────
AWT_HDR = ["Tasks", "Dy.MM RR", "Dy.MM SSP", "DRALBA RR", "DRALBA SSP",
           "PSSLB RR", "PSSLB SSP", "PSSELB RR", "PSSELB SSP", "DeRALBA RR", "DeRALBA SSP"]
AWT_ROWS = [
    ["100", "5,765.8", "2,772.2", "22,693.7", "11,328.0", "116,334.5", "57,897.5", "22,927.5", "11,324.5", "8,438.5", "4,121.1"],
    ["200", "49,874.6", "24,668.5", "61,263.2", "30,534.6", "275,424.3", "137,041.9", "65,179.7", "32,309.2", "46,702.0", "23,202.8"],
    ["300", "102,988.2", "51,186.9", "100,659.5", "50,255.3", "448,395.9", "223,455.5", "118,992.2", "59,259.2", "90,363.5", "44,994.7"],
    ["400", "133,231.8", "66,172.5", "151,684.9", "75,666.0", "665,658.3", "331,459.1", "160,237.3", "79,724.1", "135,808.3", "67,657.2"],
    ["500", "156,679.2", "77,917.0", "197,079.1", "98,246.3", "808,551.5", "402,747.9", "218,120.9", "108,575.9", "179,113.8", "89,269.3"],
    ["600", "191,008.6", "94,976.2", "246,101.1", "122,625.2", "962,942.6", "479,514.9", "271,872.6", "135,386.9", "230,371.1", "114,756.8"],
    ["700", "228,322.1", "113,516.4", "290,042.1", "144,457.9", "1,224,204.4", "609,752.6", "304,865.7", "151,751.1", "272,900.6", "135,887.0"],
    ["800", "254,545.1", "126,589.9", "334,175.5", "166,471.1", "1,362,292.0", "678,675.1", "352,715.0", "175,517.9", "313,603.2", "156,246.8"],
    ["900", "299,284.6", "148,940.1", "394,850.2", "196,937.3", "1,544,405.6", "769,353.2", "429,463.5", "213,955.4", "349,380.6", "174,111.3"],
    ["1000", "336,762.6", "167,432.3", "438,695.9", "218,642.4", "1,794,498.4", "893,700.1", "465,520.6", "231,755.8", "402,340.2", "200,398.4"],
    ["1500", "521,407.7", "259,379.7", "688,228.1", "342,754.1", "2,638,693.8", "1,314,404.0", "736,677.5", "366,742.1", "631,669.3", "314,529.6"],
    ["2000", "702,960.8", "349,808.1", "917,731.0", "457,304.4", "3,483,784.5", "1,735,493.6", "976,446.4", "486,231.8", "853,777.7", "425,255.1"],
]

AWT_IMP_HDR = ["Workload Size", "Dynamic Max-Min", "DRALBA", "PSSLB", "PSSELB", "DeRALBA"]
AWT_IMP_ROWS = [
    ["100 cloudlets", "+51.9%", "+50.1%", "+50.2%", "+50.6%", "+51.2%"],
    ["200 cloudlets", "+50.5%", "+50.2%", "+50.2%", "+50.4%", "+50.3%"],
    ["500 cloudlets", "+50.3%", "+50.1%", "+50.2%", "+50.2%", "+50.2%"],
    ["1000 cloudlets", "+50.3%", "+50.2%", "+50.2%", "+50.2%", "+50.2%"],
    ["2000 cloudlets", "+50.2%", "+50.2%", "+50.2%", "+50.2%", "+50.2%"],
    ["Overall Mean", "+50.4%", "+50.1%", "+50.2%", "+50.3%", "+50.3%"],
]

ATAT_HDR = ["Tasks", "Dy.MM RR", "Dy.MM SSP", "DRALBA RR", "DRALBA SSP",
            "PSSLB RR", "PSSLB SSP", "PSSELB RR", "PSSELB SSP", "DeRALBA RR", "DeRALBA SSP"]
ATAT_ROWS = [
    ["100", "53.78", "50.79", "62.53", "51.17", "186.59", "128.15", "80.26", "68.65", "62.92", "58.60"],
    ["200", "101.10", "75.90", "104.52", "73.79", "346.93", "208.55", "122.42", "89.55", "100.24", "76.74"],
    ["400", "184.99", "117.93", "194.97", "118.95", "740.00", "405.81", "215.35", "134.84", "185.85", "117.70"],
    ["600", "245.88", "149.85", "292.44", "168.96", "1037.74", "554.32", "329.21", "192.72", "283.55", "167.94"],
    ["800", "303.93", "175.98", "376.75", "209.05", "1433.70", "750.09", "404.86", "227.67", "362.45", "205.09"],
    ["1000", "388.61", "219.28", "483.13", "263.07", "1867.90", "967.10", "519.56", "285.79", "453.04", "251.09"],
    ["1500", "573.84", "311.81", "733.87", "388.40", "2712.77", "1388.48", "791.45", "421.51", "683.85", "366.71"],
    ["2000", "754.28", "401.13", "962.54", "502.11", "3556.92", "1808.63", "1030.06", "539.84", "904.74", "476.22"],
]

ATAT_IMP_HDR = ["Workload Size", "Dynamic Max-Min", "DRALBA", "PSSLB", "PSSELB", "DeRALBA"]
ATAT_IMP_ROWS = [
    ["100 cloudlets", "+5.6%", "+18.2%", "+31.3%", "+14.5%", "+6.9%"],
    ["200 cloudlets", "+24.9%", "+29.4%", "+39.9%", "+26.8%", "+23.4%"],
    ["400 cloudlets", "+36.2%", "+39.0%", "+45.2%", "+37.4%", "+36.7%"],
    ["600 cloudlets", "+39.1%", "+42.2%", "+46.6%", "+41.5%", "+40.8%"],
    ["800 cloudlets", "+42.1%", "+44.5%", "+47.7%", "+43.8%", "+43.4%"],
    ["1000 cloudlets", "+43.6%", "+45.5%", "+48.2%", "+45.0%", "+44.6%"],
    ["1500 cloudlets", "+45.7%", "+47.1%", "+48.8%", "+46.7%", "+46.4%"],
    ["2000 cloudlets", "+46.8%", "+47.8%", "+49.2%", "+47.6%", "+47.4%"],
    ["Overall Mean", "+36.5%", "+39.8%", "+45.1%", "+38.7%", "+37.2%"],
]

TCT_HDR = ["Tasks", "Dy.MM RR", "Dy.MM SSP", "DRALBA RR", "DRALBA SSP",
           "PSSLB RR", "PSSLB SSP", "PSSELB RR", "PSSELB SSP", "DeRALBA RR", "DeRALBA SSP"]
TCT_ROWS = [
    ["100", "5,378.0", "5,078.9", "6,253.2", "5,116.7", "18,658.7", "12,814.7", "8,026.0", "6,865.0", "6,292.1", "5,859.9"],
    ["200", "20,220.4", "15,179.4", "20,904.5", "14,757.4", "69,385.1", "41,710.2", "24,484.2", "17,910.1", "20,048.5", "15,348.6"],
    ["500", "104,291.1", "64,908.4", "120,513.7", "71,102.2", "441,043.6", "238,143.5", "136,773.0", "82,001.0", "114,919.4", "69,997.1"],
    ["1000", "388,611.8", "219,278.8", "483,128.0", "263,068.5", "1,867,902.9", "967,095.6", "519,555.2", "285,793.0", "453,043.2", "251,093.5"],
    ["2000", "1,508,569.1", "802,242.2", "1,925,088.1", "1,004,228.4", "7,113,842.1", "3,617,263.8", "2,060,111.4", "1,079,680.1", "1,809,475.2", "952,442.2"],
]

TBL7_HDR = ["Global Scheduler", "Makespan RR (s)", "Makespan SSP (s)", "Thp. RR (tasks/s)", "Thp. SSP (tasks/s)", "Energy RR (kWh)", "Energy SSP (kWh)"]
TBL7_ROWS = [
    ["Dynamic Max-Min", "1292.83", "1286.49", "1.5470", "1.5546", "2.3323", "2.3209"],
    ["DRALBA", "2061.35", "2051.25", "0.9702", "0.9750", "3.2021", "3.1864"],
    ["PSSLB", "4632.27", "4609.67", "0.4318", "0.4339", "6.8111", "6.7779"],
    ["PSSELB", "1715.43", "1707.11", "1.1659", "1.1716", "2.8926", "2.8785"],
    ["DeRALBA", "1476.24", "1469.03", "1.3548", "1.3614", "2.5566", "2.5441"],
]

REFS = [
    "[1] S. Nadeem et al., \"Runtime management of SLAs through proactive resource provisioning for a cloud environment,\" Electronics, vol. 12, no. 2, p. 296, 2023.",
    "[2] T. Hai et al., \"Task scheduling in cloud environment: Optimization, security prioritization and processor selection,\" J. Cloud Comput., vol. 12, no. 1, p. 15, 2023.",
    "[3] Y. Gu et al., \"Deep reinforcement learning for job scheduling and resource management in cloud computing: An algorithm-level review,\" arXiv:2501.01007, 2025.",
    "[4] N. Rana et al., \"A systematic literature review on contemporary and future trends in VM scheduling techniques in cloud computing,\" Frontiers Comput. Sci., vol. 6, p. 1288552, 2024.",
    "[5] C. Jiang and W. Wu, \"A fine-grained task-aware scaling mechanism for dynamic cloud workloads,\" Cluster Comput., vol. 28, no. 9, p. 560, 2025.",
    "[6] S. Bhatnagar and R. Mahant, \"Dynamic resource allocation in cloud computing environments,\" in Proc. Int. Conf. Paradigms Commun., 2025, pp. 313–328.",
    "[7] W. Zhang and H. Ou, \"Reinforcement learning based multi-objective task scheduling for energy-efficient cloud edge computing,\" Sci. Rep., vol. 15, no. 1, p. 41716, 2025.",
    "[8] R. Kumar, N. Singhal, and A. Chhabra, \"Hybrid optimization algorithm with PSO and GA for task scheduling in cloud computing,\" E-Learning Digit. Media, 2025.",
    "[9] S. O. Sati et al., \"Performance evaluation of scheduling algorithms using CloudSim,\" in Proc. Int. Conf. Netw. Commun. Intell. Comput., Springer, 2024, pp. 1157–1175.",
    "[10] Z. I. Khan, M. Khan, and S. N. M. Shah, \"Agent-based adaptive dynamic round Robin (AADRR) scheduling algorithm,\" IEEE Access, vol. 13, pp. 18308–18324, 2025.",
    "[11] K. I. Arif, \"A hybrid MinMin & round Robin approach for task scheduling in cloud computing,\" Int. J. Control Autom., vol. 13, no. 1, pp. 334–342, 2020.",
    "[12] M. Runsungnoen and T. Anusas-Amornkul, \"Round Robin scheduling based on remaining time and median (RR_RT&M),\" in Proc. SmartCom, Springer, 2019, pp. 21–29.",
    "[13] N. Ghazy et al., \"An ameliorated round Robin algorithm in the cloud computing for task scheduling,\" Bull. Electr. Eng. Informat., vol. 12, no. 2, pp. 1103–1114, 2023.",
    "[14] P. Banerjee et al., \"Comparative performance analysis of optimized round Robin scheduling (ORR),\" Int. J. Eng. Comput. Sci., vol. 8, no. 12, pp. 24890–24893, 2019.",
    "[15] J. Daood, S. Abuelenin, and S. Elmougy, \"Enhanced min-min task scheduling algorithm based on load balancing in grid computing,\" Int. J. Intell. Comput. Inf. Sci., vol. 15, no. 2, pp. 15–30, 2015.",
    "[16] Z. I. Khan, M. Khan, and S. N. M. Shah, \"MAADRR: Multi-Agent Adaptive Dynamic Round Robin for Cloud Scheduling Using Real Cloud Workload Traces,\" IEEE Access, vol. 14, pp. 44165–44184, 2026.",
    "[17] T. C. Hung et al., \"MMSIA: Improved max–min scheduling algorithm for load balancing on cloud computing,\" in Proc. 3rd Int. Conf. Mach. Learn. Soft Comput., 2019, pp. 60–64.",
    "[18] M. Runsungnoen and T. Anusas-Amornkul, \"Round Robin scheduling based on remaining time and median (RR_RT&M),\" in Proc. SmartCom, 2019, pp. 21–29.",
    "[19] N. Ghazy et al., \"An ameliorated round Robin algorithm in cloud computing for task scheduling,\" Bull. Electr. Eng. Informat., vol. 12, no. 2, pp. 1103–1114, 2023.",
    "[20] P. Banerjee et al., \"Comparative performance analysis of optimized round Robin scheduling (ORR),\" Int. J. Eng. Comput. Sci., vol. 8, no. 12, pp. 24890–24893, 2019.",
    "[21] A. K. M. M. R. Mazumder et al., \"Dynamic task scheduling algorithms in cloud computing,\" in Proc. ICECA, 2019, pp. 1280–1286.",
    "[22] S. Nabi, M. Ibrahim, and J. M. Jimenez, \"DRALBA: Dynamic and resource aware load balanced scheduling approach for cloud computing,\" IEEE Access, vol. 9, pp. 61283–61297, 2021.",
    "[23] N. Alaei and F. Safi-Esfahani, \"RePro-active: A reactive–proactive scheduling method based on simulation in cloud computing,\" J. Supercomput., vol. 74, no. 2, pp. 801–829, 2018.",
    "[24] A. Hussain et al., \"DE-RALBA: Dynamic enhanced resource aware load balancing algorithm for cloud computing,\" PeerJ Comput. Sci., vol. 11, p. e2739, 2025.",
    "[25] A. Hussain and M. Aleem, \"GoCJ: Google cloud jobs dataset for distributed and cloud computing infrastructures,\" Data, vol. 3, no. 4, p. 38, 2018.",
    "[26] M. F. Zohora, F. Farhin, and M. S. Kaiser, \"An enhanced round Robin using dynamic time quantum for real-time asymmetric burst length processes in cloud computing,\" PLoS ONE, vol. 19, no. 8, p. e0304517, 2024.",
    "[27] B. Sule, E. J. Garba, and Y. M. Malgwi, \"An enhanced dynamic time quantum mean round Robin algorithm for efficient resource allocation in cloud computing,\" Int. J. Real-Time App. Comput. Syst., vol. 3, no. 1, pp. 525–541, 2025.",
    "[28] R. Sumathi and R. M. Savithramma, \"Maximizing CPU performance: Advancing efficiency and fairness through adaptive round Robin scheduling with triple queues (ARRTQ),\" in Proc. 2nd Int. Conf. ICDSIS, 2024, pp. 1–6.",
    "[29] S. S. Priya and T. Rajendran, \"Load balancing using improved weighted round Robin algorithm in cloud computing environment,\" Int. J. Cloud Comput., vol. 13, no. 5, pp. 463–484, 2024.",
    "[30] D. Biswas et al., \"Optimized round Robin scheduling algorithm using dynamic time quantum in cloud computing,\" Int. J. Intell. Syst. Appl., vol. 15, no. 1, pp. 22–34, 2023.",
    "[31] Z. Li et al., \"Research on dynamic job shop scheduling with AGV based on DQN,\" Cluster Comput., vol. 28, no. 4, p. 236, 2025.",
    "[32] Y. Zhang et al., \"Deadline-aware online job scheduling for distributed training in heterogeneous clusters,\" IEEE Trans. Cloud Comput., vol. 13, no. 2, pp. 590–604, 2025.",
    "[33] H. G. Tani and C. El Amrani, \"Smarter round Robin scheduling algorithm for cloud computing and big data,\" J. Data Mining Digit. Humanities, p. 3104, 2018.",
    "[34] K. Ouyang et al., \"Learn from global correlations: Enhancing evolutionary algorithm via spectral GNN,\" in Proc. AAAI Conf. Artif. Intell., vol. 40, no. 29, pp. 24665–24673, 2026.",
]

# ─────────────────────────────────────────────────────────────────────────────
# 1. REPORTLAB PDF BUILDER
# ─────────────────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = letter          # 612 × 792 pt
MARGIN_H  = 0.5 * inch           # 36 pt
MARGIN_V  = 0.5 * inch           # 36 pt
COL_GAP   = 0.2 * inch           # 14.4 pt
FULL_W    = PAGE_W - 2 * MARGIN_H # 540 pt
COL_W     = (FULL_W - COL_GAP) / 2.0  # 262.8 pt


def build_pdf_styles():
    s = {}
    s['ieee_header'] = ParagraphStyle(
        'IEEEHeader', fontName='Times-Roman', fontSize=7, leading=8.5,
        alignment=TA_LEFT, spaceAfter=2)
    s['title'] = ParagraphStyle(
        'DocTitle', fontName='Times-Bold', fontSize=16, leading=19,
        alignment=TA_CENTER, spaceAfter=2)
    s['title_note'] = ParagraphStyle(
        'TitleNote', fontName='Times-Italic', fontSize=7, leading=8.5,
        alignment=TA_CENTER, spaceAfter=4)
    s['auth_name'] = ParagraphStyle(
        'AuthName', fontName='Times-Bold', fontSize=7.5, leading=9,
        alignment=TA_CENTER)
    s['auth_line'] = ParagraphStyle(
        'AuthLine', fontName='Times-Roman', fontSize=6.5, leading=7.5,
        alignment=TA_CENTER)
    s['abstract_head'] = ParagraphStyle(
        'AbsHead', fontName='Times-BoldItalic', fontSize=8, leading=10,
        alignment=TA_JUSTIFY, spaceBefore=1, spaceAfter=1)
    s['abstract_body'] = ParagraphStyle(
        'AbsBody', fontName='Times-Bold', fontSize=7.8, leading=9.8,
        alignment=TA_JUSTIFY, spaceAfter=3)
    s['keywords_head'] = ParagraphStyle(
        'KwHead', fontName='Times-BoldItalic', fontSize=7.8, leading=9.8,
        alignment=TA_JUSTIFY, spaceAfter=4)
    s['h1'] = ParagraphStyle(
        'H1', fontName='Times-Bold', fontSize=8.5, leading=11,
        alignment=TA_CENTER, spaceBefore=6, spaceAfter=2)
    s['h2'] = ParagraphStyle(
        'H2', fontName='Times-Italic', fontSize=8, leading=10,
        alignment=TA_LEFT, spaceBefore=4, spaceAfter=2)
    s['h3'] = ParagraphStyle(
        'H3', fontName='Times-Italic', fontSize=7.8, leading=9.5,
        alignment=TA_LEFT, spaceBefore=3, spaceAfter=1)
    s['body'] = ParagraphStyle(
        'Body', fontName='Times-Roman', fontSize=7.8, leading=9.8,
        alignment=TA_JUSTIFY, firstLineIndent=8, spaceAfter=2.5)
    s['body_noi'] = ParagraphStyle(
        'BodyNoI', fontName='Times-Roman', fontSize=7.8, leading=9.8,
        alignment=TA_JUSTIFY, firstLineIndent=0, spaceAfter=2)
    s['bullet'] = ParagraphStyle(
        'Bullet', fontName='Times-Roman', fontSize=7.8, leading=9.8,
        alignment=TA_JUSTIFY, leftIndent=8, firstLineIndent=-6, spaceAfter=1.5)
    s['eq'] = ParagraphStyle(
        'Eq', fontName='Times-Italic', fontSize=7.8, leading=10,
        alignment=TA_CENTER, spaceBefore=1.5, spaceAfter=1.5)
    s['caption'] = ParagraphStyle(
        'Caption', fontName='Times-Roman', fontSize=7.2, leading=9,
        alignment=TA_CENTER, spaceAfter=3, spaceBefore=2)
    s['table_head'] = ParagraphStyle(
        'TableHead', fontName='Times-Bold', fontSize=7.2, leading=9,
        alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)
    s['code'] = ParagraphStyle(
        'Code', fontName='Courier', fontSize=5.3, leading=6.8,
        alignment=TA_LEFT, spaceAfter=1, spaceBefore=1)
    s['ref'] = ParagraphStyle(
        'Ref', fontName='Times-Roman', fontSize=6.2, leading=7.6,
        alignment=TA_JUSTIFY, leftIndent=10, firstLineIndent=-10, spaceAfter=1.2)
    s['tbl_hdr'] = ParagraphStyle(
        'TblHdr', fontName='Times-Bold', fontSize=5.8, leading=7.2,
        alignment=TA_CENTER)
    s['tbl_cell'] = ParagraphStyle(
        'TblCell', fontName='Times-Roman', fontSize=5.8, leading=7.2,
        alignment=TA_CENTER)
    s['tbl_cell_l'] = ParagraphStyle(
        'TblCellL', fontName='Times-Roman', fontSize=5.8, leading=7.2,
        alignment=TA_LEFT)
    s['insight'] = ParagraphStyle(
        'Insight', fontName='Times-Italic', fontSize=7.2, leading=9,
        alignment=TA_JUSTIFY, leftIndent=4, firstLineIndent=0, spaceAfter=2.5)
    return s


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for i, state in enumerate(self._saved, 1):
            self.__dict__.update(state)
            self.setFont("Times-Roman", 7.5)
            self.drawCentredString(PAGE_W / 2, 18, str(i))
            super().showPage()
        super().save()


def hcell(text, styles, bold=False, left=False):
    if bold:
        st = styles['tbl_hdr']
    elif left:
        st = styles['tbl_cell_l']
    else:
        st = styles['tbl_cell']
    return Paragraph(str(text), st)


def build_pdf_story(styles):
    B = styles['body']
    BN = styles['body_noi']
    BL = styles['bullet']
    H1 = styles['h1']
    H2 = styles['h2']
    H3 = styles['h3']
    CA = styles['caption']
    TH = styles['table_head']
    IN = styles['insight']
    RF = styles['ref']

    def sp(h): return Spacer(1, h)
    def hr(): return HRFlowable(width="100%", thickness=0.4, color=colors.HexColor('#666666'), spaceBefore=2, spaceAfter=2)
    def eq(txt, n=""):
        label = f"({n})" if n else ""
        t = Table([[Paragraph(f"<i>{txt}</i>", styles['eq']),
                    Paragraph(f"<b>{label}</b>", ParagraphStyle('EqR', fontName='Times-Roman', fontSize=7.5, alignment=TA_RIGHT))]],
                  colWidths=[220, 42])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        return t

    story = []

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 1 HEADER (Title and 6 Author Boxes matching IEEE template)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("XXX-X-XXXX-XXXX-X/XX/$XX.00 ©20XX IEEE", styles['ieee_header']))
    story.append(Paragraph(
        "<b>SSP-ARR: Stability-Switched Predictive Adaptive Round Robin for Multi-Tier "
        "Cloud Task Scheduling Using Real-World Cloud Workload Traces</b>", styles['title']))
    story.append(Paragraph("*Note: Sub-titles are not captured in Xplore and should not be used", styles['title_note']))

    # 6 Author Slots in 3 columns (matching page 1 screenshot)
    def auth_cell(num_str):
        return [
            Paragraph(f"line 1: {num_str} Given Name Surname", styles['auth_name']),
            Paragraph("line 2: dept. name of organization", styles['auth_line']),
            Paragraph("(of Affiliation)", styles['auth_line']),
            Paragraph("line 3: name of organization (of Affiliation)", styles['auth_line']),
            Paragraph("line 4: City, Country", styles['auth_line']),
            Paragraph("line 5: email address or ORCID", styles['auth_line']),
        ]

    author_table_data = [
        [auth_cell("1<sup>st</sup>"), auth_cell("2<sup>nd</sup>"), auth_cell("3<sup>rd</sup>")],
        [auth_cell("4<sup>th</sup>"), auth_cell("5<sup>th</sup>"), auth_cell("6<sup>th</sup>")]
    ]
    t_auth = Table(author_table_data, colWidths=[180, 180, 180])
    t_auth.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(t_auth)

    # Move from Page 1 Header Frame to Column 1 Frame
    story.append(FrameBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 1 COLUMN 1: ABSTRACT, KEYWORDS, INTRODUCTION
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph(
        "<b><i>Abstract</i>—Task scheduling in heterogeneous cloud datacenters plays a decisive role in maximizing computational "
        "resource efficiency, reducing end-user latency, and lowering datacenter energy footprint. However, conventional time-sharing "
        "schedulers—predominantly Classical Round Robin (RR) and its static variants—rely on rigid, pre-configured CPU time quanta. "
        "Under burst-heavy, heterogeneous, and unpredictable cloud workloads, fixed time-slicing causes severe head-of-line blocking "
        "(the convoy effect), excessive context-switching overhead, and inflated waiting times. While reactive adaptive schedulers "
        "(such as MAADRR) compute median-based time quanta, purely reactive heuristics exhibit latency lag during sudden workload phase "
        "transitions and fail to anticipate high-variance task arrivals. To overcome these limitations, this paper proposes SSP-ARR "
        "(Stability-Switched Predictive Adaptive Round Robin), an intelligent, multi-tier scheduling framework tailored for heterogeneous "
        "cloud infrastructures. SSP-ARR dynamically evaluates workload volatility at the local VM tier using a sliding-window Coefficient "
        "of Variation (CV). When queue variance remains stable (CV &le; 0.50), the scheduler operates in a safe queue-median reactive mode; "
        "when volatility surges (CV &gt; 0.50), it transitions to an adaptive Exponentially Weighted Moving Average (EWMA) predictive mode "
        "governed by an error-modulated learning rate and strict confidence gating (Normalized Prediction Error &le; 0.20). Furthermore, "
        "task queues are structured under Shortest Remaining Processing Time (SRPT) ordering with bounded quantum clamping [0.001 s, 60.0 s]. "
        "SSP-ARR is evaluated across five state-of-the-art global dispatching strategies (Dynamic Max-Min, DRALBA, PSSLB, PSSELB, and DeRALBA) "
        "using real-world Google Cloud Jobs (GoCJ) traces spanning 100 to 2000 cloudlets on CloudSim Plus 8.5.7. Experimental results "
        "demonstrate that SSP-ARR achieves an average reduction of ~50.2% in Average Waiting Time (AWT), up to 49.2% improvement in Average "
        "Turnaround Time (ATAT), saves millions of cumulative completion seconds in Total Completion Time (TCT), and yields superior makespan, "
        "throughput, and SPECpower-modeled energy efficiency compared to Classical RR across all global policies.</b>", styles['abstract_body']))

    story.append(Paragraph(
        "<b><i>Keywords</i>—Cloud task scheduling, multi-tier architecture, adaptive dynamic time quantum, stability switching, "
        "coefficient of variation, EWMA prediction, GoCJ workload traces, CloudSim Plus.</b>", styles['keywords_head']))

    story.append(Paragraph("I. INTRODUCTION", H1))
    story.append(Paragraph(
        "Cloud computing platforms have emerged as the foundational utility for modern enterprise IT, scientific computing, "
        "and consumer applications [1], [2]. The elastic resource model allows providers to multiplex massive pools of virtualized "
        "compute, memory, and network resources among thousands of concurrently competing client workloads [3], [4]. In this environment, "
        "task scheduling is decisive in determining whether a cloud provider can satisfy Service Level Agreements (SLAs), minimize operating "
        "costs, and prevent severe server thermal dissipation [5], [6].", B))
    story.append(Paragraph(
        "Task scheduling in cloud computing typically operates across a two-tier hierarchy [7], [8]. At the first tier, global broker "
        "schedulers receive incoming user tasks and map them to appropriate Virtual Machines (VMs) across distributed datacenters [9]. At the "
        "second tier, local VM hypervisor schedulers manage the execution sequence of cloudlets residing in each VM's circular ready queue [10]. "
        "While substantial research has focused on global heuristic and metaheuristic dispatchers, the efficiency of local VM scheduling "
        "remains the critical determinant of actual CPU core utilization, context-switching overhead, and task waiting times [11], [12].", B))
    story.append(Paragraph(
        "At the local VM level, Classical Round Robin (RR) has historically been the default choice due to its simplicity, starvation prevention, "
        "and conceptual fairness [13], [14]. However, Classical RR is burdened by a critical architectural limitation: reliance on a static, "
        "pre-configured Time Quantum (TQ). If the quantum is set too small, the system suffers severe throughput degradation from frequent "
        "CPU context switches [15]. Conversely, if the quantum is set too large, Classical RR degenerates into First-Come First-Served (FCFS), "
        "causing short tasks to stall behind long, compute-heavy jobs—an anomaly known as the convoy effect [16].", B))
    story.append(Paragraph(
        "Recent advances have attempted to mitigate this trade-off by introducing dynamic time quantum adaptation, such as the Multi-Agent "
        "Adaptive Dynamic Round Robin (MAADRR) scheduler [16]. MAADRR dynamically computes the time quantum as the median of task burst lengths "
        "in the VM queue. While MAADRR improves upon static RR under moderate conditions, its purely reactive formulation exhibits severe latency "
        "lag during rapid workload phase changes and fails to anticipate task burst variance under volatile real-world traffic.", B))
    story.append(Paragraph(
        "To resolve these challenges, this paper presents <b>SSP-ARR</b> (<b>S</b>tability-<b>S</b>witched <b>P</b>redictive <b>A</b>daptive "
        "<b>R</b>ound <b>R</b>obin), an intelligent local VM scheduling framework that incorporates continuous variance sensing, dual-mode "
        "reactive/predictive quantum selection, confidence gating, and bounded preemption clamping within a multi-tier cloud hierarchy.", B))
    story.append(Paragraph("The key contributions of this paper are summarized as follows:", BN))
    story.append(Paragraph("1. <b>Stability-Switched Dual-Engine</b>: Continuous tracking of Coefficient of Variation (CV = &sigma;/&mu;) over sliding history window (W = 5) to isolate burst volatility.", BL))
    story.append(Paragraph("2. <b>Confidence-Gated EWMA Prediction</b>: Adaptive error-modulated learning rate (&alpha; &isin; [0.20, 0.80]) with strict confidence gating (NPE &le; 20%) to prevent forecasting drift.", BL))
    story.append(Paragraph("3. <b>Multi-Tier Orthogonality</b>: Evaluated across five leading global dispatchers (Dy.MM, DRALBA, PSSLB, PSSELB, DeRALBA), demonstrating consistent ~50.2% AWT reduction.", BL))
    story.append(Paragraph("4. <b>Rigorous Trace-Driven Benchmark</b>: CloudSim Plus 8.5.7 evaluation with real GoCJ traces (100–2000 cloudlets) across seven key QoS and energy metrics.", BL))

    story.append(Paragraph("II. RELATED WORK &amp; ARCHITECTURAL EVOLUTION", H1))
    story.append(Paragraph("A. Adaptive Round Robin Variants", H2))
    story.append(Paragraph(
        "Dynamic time quantum adaptation has received extensive research interest. In [17], the authors proposed a hybrid Min-Min and Round "
        "Robin algorithm to combine makespan minimization with fairness. Runsungnoen and Anusas-Amornkul [18] developed the RR_RT&amp;M technique "
        "using remaining task execution time and median estimation. Ghazy et al. [19] formulated an ameliorated Round Robin algorithm calculating "
        "quantum based on arithmetic mean of remaining bursts. Banerjee et al. [20] presented Optimized Round Robin (ORR), proving that dynamic "
        "time quantum selection significantly mitigates average waiting time. Mazumder et al. [21] introduced Priority-based Round Robin (PRR) "
        "prioritizing tasks according to burst length and deadline thresholds.", B))
    story.append(Paragraph("B. Multi-Tier Global Schedulers", H2))
    story.append(Paragraph(
        "Global schedulers govern cloudlet distribution across heterogeneous VMs. Five representative global dispatching strategies "
        "are considered: (1) <b>Dynamic Max-Min (Dy. MM)</b> [17]; (2) <b>DRALBA</b> [22], a resource-aware load-balancing algorithm; "
        "(3) <b>PSSLB</b> [23], a priority-based queue-state algorithm; (4) <b>PSSELB</b> [23], an energy-aware variant of PSSLB; and "
        "(5) <b>DeRALBA</b> [24], integrating dispersion thresholding with adaptive candidate matching.", B))

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 2: TWO-COLUMN (TABLE I, ARCHITECTURE, FIG 1, MATH FORMULATION, ALGO 1)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("C. Evolution from Classical RR and MAADRR to SSP-ARR", H2))
    story.append(Paragraph(
        "Existing local schedulers fall into two flawed extremes: static allocation (RR) or unconstrained reactive heuristics (MAADRR). "
        "Neither architecture explicitly measures queue burst variance or employs predictive models to anticipate burst length trends. "
        "Table I highlights the evolutionary progression from Classical RR and MAADRR to SSP-ARR.", B))

    # TABLE I: Fits inside Column Width (262.8 pt)
    t1_data = [
        [hcell("Feature", styles, True), hcell("Classical RR", styles, True), hcell("MAADRR [16]", styles, True), hcell("Proposed SSP-ARR", styles, True)],
        [hcell("Quantum Sizing", styles, True, True), hcell("Static (1.0 s)", styles), hcell("Dynamic Median", styles), hcell("Dual Reactive/Predictive", styles, True)],
        [hcell("Workload Sensing", styles, True, True), hcell("None", styles), hcell("Reactive only", styles), hcell("CV Stability (θ_CV=0.50)", styles, True)],
        [hcell("Burst Prediction", styles, True, True), hcell("None", styles), hcell("None", styles), hcell("Adaptive EWMA", styles, True)],
        [hcell("Confidence Gate", styles, True, True), hcell("None", styles), hcell("None", styles), hcell("NPE ≤ 0.20 Gating", styles, True)],
        [hcell("Queue Ordering", styles, True, True), hcell("FIFO", styles), hcell("Priority-Sort", styles), hcell("SRPT Ascending", styles, True)],
        [hcell("Quantum Clamping", styles, True, True), hcell("Fixed", styles), hcell("Unbounded", styles), hcell("[0.001 s, 60.0 s]", styles, True)],
        [hcell("Preemption Penalty", styles, True, True), hcell("High (Severe)", styles), hcell("Moderate", styles), hcell("Minimal (Consolidated)", styles, True)],
        [hcell("Global Tier Support", styles, True, True), hcell("Single-tier", styles), hcell("Multi-agent", styles), hcell("5 Global Schedulers", styles, True)],
    ]
    t1 = Table(t1_data, colWidths=[62, 54, 66, 80])
    t1.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 5.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    story.append(Paragraph("TABLE I. ARCHITECTURAL COMPARISON ACROSS SCHEDULING MODELS", TH))
    story.append(t1)
    story.append(sp(4))

    # SECTION III: MATHEMATICAL DESIGN
    story.append(Paragraph("III. MATHEMATICAL DESIGN AND ALGORITHMIC FORMULATION", H1))
    story.append(Paragraph("A. Multi-Tier System Architecture", H2))
    story.append(Paragraph(
        "The proposed architecture operates across two coordinated layers: (1) Tier-1 Global Datacenter Dispatching maps "
        "submitted cloudlets to VMs using established global balancing policies; (2) Tier-2 Local VM Scheduling governs cloudlet "
        "preemption and execution via SSP-ARR, illustrated in Fig. 1.", B))

    # Embedded Figure 1 (Architecture diagram: fits single column 250 pt width)
    fig1_path = os.path.join(FIGURES_DIR, "fig1_architecture.png")
    if os.path.exists(fig1_path):
        story.append(RLImage(fig1_path, width=250, height=342))
        story.append(Paragraph("Fig. 1. Architectural workflow of the proposed SSP-ARR multi-tier framework.", CA))
    story.append(sp(4))

    # Move to Column 2 of Page 2
    story.append(FrameBreak())

    story.append(Paragraph("B. Workload Volatility Sensing via CV", H2))
    story.append(Paragraph(
        "For each VM v_j, let H_j = {B_{j,1}, ..., B_{j,W}} represent execution bursts of the last W completed cloudlets (W = 5). "
        "The local agent tracks sample mean &mu;_j and sample standard deviation &sigma;_j:", BN))
    story.append(eq("&mu;<sub>j</sub> = (1/W) &middot; &Sigma; B<sub>j,k</sub>", "1"))
    story.append(eq("&sigma;<sub>j</sub> = &radic;[ (1/W) &middot; &Sigma; (B<sub>j,k</sub> &minus; &mu;<sub>j</sub>)<sup>2</sup> ]", "2"))
    story.append(Paragraph("The Coefficient of Variation (CV_j) is defined as:", BN))
    story.append(eq("CV<sub>j</sub> = &sigma;<sub>j</sub> / &mu;<sub>j</sub>", "3"))
    story.append(Paragraph("&bull; <b>Stable Regime</b> (CV_j &le; &theta;<sub>CV</sub>): Low dispersion (&theta;<sub>CV</sub> = 0.50). The scheduler selects Safe Reactive Mode.", BN))
    story.append(Paragraph("&bull; <b>Volatile Regime</b> (CV_j &gt; &theta;<sub>CV</sub>): High burst variability. The scheduler activates Predictive EWMA Mode.", BN))

    story.append(Paragraph("C. Dual-Mode Quantum Allocation Engine", H2))
    story.append(Paragraph("<i>1) Safe Reactive Mode (CV_j &le; &theta;<sub>CV</sub>)</i>: The quantum is computed as the median of remaining bursts (RB) in ready queue Q_j plus candidate task t:", BN))
    story.append(eq("Q<sub>reactive</sub> = median( {RB(x) : x &isin; Q<sub>j</sub>} &cup; {RB(t)} )", "4"))
    story.append(Paragraph("<i>2) Predictive EWMA Mode (CV_j &gt; &theta;<sub>CV</sub>)</i>: The expected optimal burst duration is forecasted using an Exponentially Weighted Moving Average:", BN))
    story.append(eq("B<sub>pred,j,t+1</sub> = &alpha;<sub>t</sub> &middot; B<sub>j,t</sub> + (1 &minus; &alpha;<sub>t</sub>) &middot; B<sub>pred,j,t</sub>", "5"))
    story.append(Paragraph("where &alpha;<sub>t</sub> is an adaptive error-modulated learning rate:", BN))
    story.append(eq("&alpha;<sub>t</sub> = 0.20 if NPE &lt; 0.10  |  0.40 if 0.10 &le; NPE &lt; 0.20", "6a"))
    story.append(eq("&alpha;<sub>t</sub> = 0.60 if 0.20 &le; NPE &lt; 0.30  |  0.80 if NPE &ge; 0.30", "6b"))
    story.append(Paragraph("<i>3) Normalized Prediction Error (NPE) and Confidence Gating</i>:", BN))
    story.append(eq("NPE<sub>t</sub> = |B<sub>j,t</sub> &minus; B<sub>pred,j,t</sub>| / B<sub>j,t</sub>", "7"))
    story.append(Paragraph("To guarantee stability, predictions are gated by confidence threshold &tau;<sub>gate</sub> = 0.20:", BN))
    story.append(eq("Q<sub>selected</sub> = B<sub>pred,j,t+1</sub>  if (CV<sub>j</sub> &gt; 0.50 and NPE<sub>t</sub> &le; 0.20)", "8a"))
    story.append(eq("Q<sub>selected</sub> = Q<sub>reactive</sub>   otherwise (fallback to median)", "8b"))
    story.append(Paragraph("<i>4) Boundary Clamping</i>: Quantum is clamped within [Q_min = 0.001 s, Q_max = 60.0 s]:", BN))
    story.append(eq("Q<sub>j</sub> = max(Q<sub>min</sub>, min(Q<sub>max</sub>, min(Q<sub>selected</sub>, RB(t))))", "9"))

    story.append(Paragraph("D. Formal Algorithmic Pseudocode", H2))
    # Code snippet in table
    code_text = (
        "Algorithm 1: Multi-Tier Cloud Task Scheduling with SSP-ARR\n"
        "Input : Cloudlet set C = {c_1..c_n}; VM pool V = {v_1..v_m};\n"
        "        Global policy P in {Dy.MM, DRALBA, PSSLB, PSSELB, DeRALBA};\n"
        "        Q_min=0.001s, Q_max=60.0s; δ_cs=0.005s; θ_CV=0.50; τ_gate=0.20.\n"
        "// TIER 1: Global Datacenter Dispatching\n"
        "1: Assignment[] ← GlobalSchedulers.assign(P, C, V);\n"
        "2: Enqueue tasks to VM ready queues Q_1..Q_m;\n"
        "// TIER 2: Local SSP-ARR Execution per VM\n"
        "3: for each VM v_j with queue Q_j do\n"
        "4:   Sort Q_j in ascending order of burst (SRPT order);\n"
        "5:   while Q_j is not empty do\n"
        "6:     t ← Q_j.pollHead();\n"
        "7:     q_med ← median(Q_j, t);  cv ← ComputeCV(history);\n"
        "8:     if cv > θ_CV and npe ≤ τ_gate then q ← ewma;\n"
        "9:     else q ← q_med; end if\n"
        "10:    slice ← min(max(Q_min, min(Q_max, q)), t.remainingBurst);\n"
        "11:    t.remainingBurst -= slice; currentTime += slice;\n"
        "12:    if t.remainingBurst ≤ 1e-9 then\n"
        "13:      RecordCompletionStats(t); UpdateEWMA(t.burst);\n"
        "14:    else\n"
        "15:      currentTime += δ_cs; InsertSorted(Q_j, t);\n"
        "16:    end if\n"
        "17:  end while\n"
        "18: end for"
    )
    t_code = Table([[Preformatted(code_text, styles['code'])]], colWidths=[260])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F4F6F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_code)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 3: TWO-COLUMN (TABLE II, SECTION IV, TABLE III, SECTION V.A)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("E. Table of Symbols and Notations", H2))
    sym_data = [
        [hcell("Symbol", styles, True), hcell("Definition", styles, True)],
        [hcell("VM_j, Q_j", styles, False, True), hcell("j-th VM and its circular ready queue", styles, False, True)],
        [hcell("c_i, L_i", styles, False, True), hcell("i-th cloudlet and instruction length (MI)", styles, False, True)],
        [hcell("MIPS_j, RB", styles, False, True), hcell("VM processing speed and remaining burst (s)", styles, False, True)],
        [hcell("CV_j, θ_CV", styles, False, True), hcell("Coefficient of Variation and stability threshold (0.50)", styles, False, True)],
        [hcell("B_pred, α_t", styles, False, True), hcell("EWMA predicted burst and adaptive learning rate [0.2, 0.8]", styles, False, True)],
        [hcell("NPE, τ_gate", styles, False, True), hcell("Normalized Prediction Error and confidence gate (0.20)", styles, False, True)],
        [hcell("Q_min, Q_max", styles, False, True), hcell("Bounded quantum limits (0.001 s and 60.0 s)", styles, False, True)],
        [hcell("δ_cs", styles, False, True), hcell("Context switching penalty (0.005 s / 5 ms)", styles, False, True)],
        [hcell("T_i, A_i, B_i", styles, False, True), hcell("Completion time, arrival time, burst time of task i", styles, False, True)],
        [hcell("P_idle, P_max", styles, False, True), hcell("Idle and peak power per physical host (150 W and 250 W)", styles, False, True)],
    ]
    t_sym = Table(sym_data, colWidths=[65, 195])
    t_sym.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 5.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("TABLE II. MATHEMATICAL SYMBOLS AND NOTATIONS", TH))
    story.append(t_sym)
    story.append(sp(4))

    # SECTION IV: EXPERIMENTAL SETUP
    story.append(Paragraph("IV. EXPERIMENTAL SETUP &amp; PERFORMANCE EVALUATION", H1))
    story.append(Paragraph("A. Cloud Simulation Environment", H2))
    story.append(Paragraph(
        "The experimental framework is implemented using <b>CloudSim Plus 8.5.7</b> on <b>Java 21</b>. CloudSim Plus provides "
        "fully extensible abstractions for datacenter brokers, host power profiles, and VM time-shared schedulers.", B))

    story.append(Paragraph("B. Infrastructure &amp; Heterogeneous VM Specifications", H2))
    story.append(Paragraph(
        "The physical datacenter comprises <b>30 physical hosts</b> (120 PEs total @ 4000 MIPS each), 32 GB RAM, 100 Gbps network, "
        "and 1 TB storage. Host power consumption follows the linear SPECpower standard server model:", B))
    story.append(eq("P_host(u) = P_idle + (P_max − P_idle) · u", "10"))
    story.append(Paragraph(
        "where P_idle = 150 W, P_max = 250 W, and u &isin; [0, 1] is CPU utilization fraction. A pool of <b>80 heterogeneous VMs</b> "
        "is instantiated with speeds from 1000 to 4000 MIPS (step 200 MIPS).", B))

    story.append(Paragraph("C. Benchmark Workload: Google Cloud Jobs (GoCJ)", H2))
    story.append(Paragraph(
        "The framework is evaluated using real-world <b>Google-Cluster-like Job (GoCJ)</b> traces [25], exhibiting realistic arrival "
        "bursts, asymmetric lengths, and high variance (CV &asymp; 1.24). Evaluations span 12 workload scales: 100 to 2000 cloudlets (15,000–900,000 MI).", B))

    # Move to Column 2 of Page 3
    story.append(FrameBreak())

    # Table III: Parameters
    tbl3_data = [
        [hcell("Parameter", styles, True), hcell("Configuration Value", styles, True)],
        [hcell("Simulation Engine", styles, True, True), hcell("CloudSim Plus 8.5.7 (Java 21)", styles, False, True)],
        [hcell("Physical Datacenter", styles, True, True), hcell("30 Hosts (120 PEs total, 4 PEs/Host @ 4000 MIPS)", styles, False, True)],
        [hcell("Host Power Profile", styles, True, True), hcell("SPECpower Model (P_idle=150W, P_max=250W)", styles, False, True)],
        [hcell("Virtual Machines", styles, True, True), hcell("80 Heterogeneous VMs (1000–4000 MIPS)", styles, False, True)],
        [hcell("VM Memory / BW", styles, True, True), hcell("8192 MB RAM, 20,000 Mbps Bandwidth", styles, False, True)],
        [hcell("Workload Benchmark", styles, True, True), hcell("Real-world Google Cloud Jobs (GoCJ)", styles, False, True)],
        [hcell("Workload Sizes", styles, True, True), hcell("100, 200, 300..1000, 1500, 2000 cloudlets", styles, False, True)],
        [hcell("Global Schedulers", styles, True, True), hcell("Dynamic Max-Min, DRALBA, PSSLB, PSSELB, DeRALBA", styles, False, True)],
        [hcell("Local Schedulers", styles, True, True), hcell("Classical RR (Fixed q=1.0s, FIFO) vs. SSP-ARR", styles, False, True)],
        [hcell("Context Switch Penalty", styles, True, True), hcell("δ_cs = 0.005 s (5 ms) per preemption", styles, False, True)],
        [hcell("Evaluation Runs", styles, True, True), hcell("3 independent runs per size (mean reported)", styles, False, True)],
    ]
    t3 = Table(tbl3_data, colWidths=[98, 162])
    t3.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 5.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("TABLE III. SIMULATION ENVIRONMENT PARAMETERS", TH))
    story.append(t3)
    story.append(sp(4))

    story.append(Paragraph("D. Performance Metrics", H2))
    story.append(Paragraph("Evaluated using seven standard performance metrics:", BN))
    story.append(Paragraph("1. <b>Average Waiting Time (AWT)</b>:", BL))
    story.append(eq("AWT = (1/N) · Σ (T_i − A_i − B_i)", "11"))
    story.append(Paragraph("2. <b>Average Turnaround Time (ATAT)</b>:", BL))
    story.append(eq("ATAT = (1/N) · Σ (T_i − A_i)", "12"))
    story.append(Paragraph("3. <b>Average Completion Time (ACT)</b>: Mean end-to-end task completion duration.", BL))
    story.append(Paragraph("4. <b>Total Completion Time (TCT)</b>:", BL))
    story.append(eq("TCT = Σ T_i = N × ACT", "13"))
    story.append(Paragraph("5. <b>System Throughput (Thp)</b>:", BL))
    story.append(eq("Throughput = N / Makespan  (tasks/second)", "14"))
    story.append(Paragraph("6. <b>Host Energy Consumption (E_total)</b>:", BL))
    story.append(eq("E_total = (1/3,600,000) · Σ ∫P_j(t) dt  (kWh)", "15"))
    story.append(Paragraph("7. <b>Makespan (T_max)</b>: Total wall-clock duration (max<sub>i</sub> T<sub>i</sub>).", BL))
    story.append(Paragraph("Percentage improvement formulas:", BN))
    story.append(eq("Imp_lower-better (%) = (X_RR − X_SSP) / X_RR × 100", "16"))
    story.append(eq("Imp_higher-better (%) = (X_SSP − X_RR) / X_RR × 100", "17"))

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 4: FULL-WIDTH (TABLE IV, FIG 2, TABLE V, SECTION V.B, TABLE VII)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(NextPageTemplate('FullWidth'))
    story.append(PageBreak())

    story.append(Paragraph("V. RESULTS AND COMPARATIVE PERFORMANCE ANALYSIS", H1))
    story.append(Paragraph("A. Average Waiting Time (AWT)", H2))
    story.append(Paragraph(
        "Average Waiting Time directly reflects queue congestion and the elimination of the convoy effect. "
        "Table IV presents the raw AWT values (in milliseconds) and Table V presents percentage improvements of SSP-ARR over Classical RR "
        "across all five global scheduling strategies under 100 to 2000 GoCJ cloudlets.", BN))

    cw_full = [44] + [49.6] * 10
    t4_data = [[hcell(h, styles, True) for h in AWT_HDR]]
    for row in AWT_ROWS:
        t4_data.append([hcell(v, styles) for v in row])

    t4 = Table(t4_data, colWidths=cw_full)
    t4.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    story.append(Paragraph("TABLE IV. COMPARISON OF AWT (MS) FOR RR AND SSP-ARR (100–2000 GOCJ CLOUDLETS)", TH))
    story.append(t4)
    story.append(sp(3))

    # Embedded Figure 2 (AWT Graph: 530 pt wide x 195 pt high)
    fig2_path = os.path.join(FIGURES_DIR, "fig2_awt_comparison.png")
    if os.path.exists(fig2_path):
        story.append(RLImage(fig2_path, width=530, height=195))
        story.append(Paragraph(
            "Fig. 2. Average Waiting Time (AWT) comparison between Classical RR and SSP-ARR across five global scheduling strategies under "
            "100 to 2000 GoCJ cloudlets: (a) Dy.MM, DRALBA, and DeRALBA; (b) PSSLB and PSSELB.", CA))
    story.append(sp(2))

    # TABLE V: AWT Percentage Improvement
    t5_imp_data = [[hcell(h, styles, True) for h in AWT_IMP_HDR]]
    for row in AWT_IMP_ROWS:
        t5_imp_data.append([hcell(v, styles) for v in row])
    t5_imp = Table(t5_imp_data, colWidths=[90, 90, 90, 90, 90, 90])
    t5_imp.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    story.append(Paragraph("TABLE V. PERCENTAGE IMPROVEMENT IN AWT (SSP-ARR OVER CLASSICAL RR)", TH))
    story.append(t5_imp)
    story.append(sp(2))
    story.append(Paragraph(
        "<i>Key Insight: Across all 12 workload scales and all five global dispatchers, SSP-ARR consistently reduces "
        "Average Waiting Time by ~50.2%. Under heavy scale (2000 tasks), PSSLB AWT drops from 3,483,784.5 ms to "
        "1,735,493.6 ms, and Dynamic Max-Min drops from 702,960.8 ms to 349,808.1 ms. By ranking queues via SRPT and "
        "applying predictive quanta, short jobs complete without lingering in queue lines behind massive bursts.</i>", IN))

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 5: FULL-WIDTH (TABLE VI, FIG 3, TABLE VII, SECTION V.C, TABLE VIII)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("B. Average Turnaround Time (ATAT) &amp; Average Completion Time (ACT)", H2))
    story.append(Paragraph(
        "Table VI summarizes ATAT results (in seconds) across all evaluated strategies. ATAT reflects the total duration from task arrival to completion.", BN))

    t6_data = [[hcell(h, styles, True) for h in ATAT_HDR]]
    for row in ATAT_ROWS:
        t6_data.append([hcell(v, styles) for v in row])
    t6 = Table(t6_data, colWidths=cw_full)
    t6.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    story.append(Paragraph("TABLE VI. COMPARISON OF ATAT (S) FOR RR AND SSP-ARR ACROSS FIVE GLOBAL SCHEDULERS", TH))
    story.append(t6)
    story.append(sp(2))

    # Embedded Figure 3 (ATAT Graph: 530 pt wide x 170 pt high)
    fig3_path = os.path.join(FIGURES_DIR, "fig3_atat_comparison.png")
    if os.path.exists(fig3_path):
        story.append(RLImage(fig3_path, width=530, height=170))
        story.append(Paragraph(
            "Fig. 3. Average Turnaround Time (ATAT) performance: (a) Absolute ATAT for Dy.MM and DRALBA; "
            "(b) Load-proportional percentage improvement scaling from +5.6% up to +49.2%.", CA))
    story.append(sp(2))

    # TABLE VII: ATAT Imp
    t7_imp_data = [[hcell(h, styles, True) for h in ATAT_IMP_HDR]]
    for row in ATAT_IMP_ROWS:
        t7_imp_data.append([hcell(v, styles) for v in row])
    t7_imp = Table(t7_imp_data, colWidths=[90, 90, 90, 90, 90, 90])
    t7_imp.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    story.append(Paragraph("TABLE VII. PERCENTAGE IMPROVEMENT IN ATAT (SSP-ARR OVER CLASSICAL RR)", TH))
    story.append(t7_imp)
    story.append(sp(2))

    # TABLE VIII: TCT
    story.append(Paragraph("C. Total Completion Time (TCT)", H2))
    story.append(Paragraph(
        "Total Completion Time aggregates the finish timestamps across all N cloudlets (TCT = Σ T_i). Table VIII highlights "
        "the massive cumulative seconds saved by SSP-ARR.", BN))
    tct_table_data = [[hcell(h, styles, True) for h in TCT_HDR]]
    for row in TCT_ROWS:
        tct_table_data.append([hcell(v, styles) for v in row])
    t_tct = Table(tct_table_data, colWidths=cw_full)
    t_tct.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    story.append(Paragraph("TABLE VIII. COMPARISON OF TCT (SECONDS) FOR RR AND SSP-ARR ACROSS FIVE GLOBAL SCHEDULERS", TH))
    story.append(t_tct)
    story.append(sp(2))
    story.append(Paragraph(
        "<i>Key Insight: At 2000 cloudlets, SSP-ARR reduces cumulative cloudlet execution time under PSSLB from 7.11 million "
        "seconds to 3.61 million seconds (saving 3.49 million task seconds). Under Dynamic Max-Min, completion drops from "
        "1.508 million seconds to 802,242 seconds (saving 706,326 seconds), proving substantial aggregate latency reductions.</i>", IN))

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 6: FULL-WIDTH (TABLE IX, FIG 4, V.E KEY MECHANISMS)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("D. Makespan, System Throughput, and Host Energy Consumption", H2))
    story.append(Paragraph(
        "Table IX compares cluster Makespan, System Throughput, and SPECpower-modeled Host Energy Consumption at the maximum "
        "benchmark load of 2000 GoCJ cloudlets.", BN))
    t9_data = [[hcell(h, styles, True) for h in TBL7_HDR]]
    for row in TBL7_ROWS:
        t9_data.append([hcell(row[0], styles, True, True)] + [hcell(v, styles) for v in row[1:]])
    t9 = Table(t9_data, colWidths=[90, 75, 75, 75, 75, 75, 75])
    t9.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D8E4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    story.append(Paragraph("TABLE IX. PERFORMANCE SUMMARY OF MAKESPAN, THROUGHPUT, AND ENERGY AT 2000 GOCJ CLOUDLETS", TH))
    story.append(t9)
    story.append(sp(2))

    # Embedded Figure 4 (TCT & Energy: 530 pt wide x 170 pt high)
    fig4_path = os.path.join(FIGURES_DIR, "fig4_tct_and_cluster.png")
    if os.path.exists(fig4_path):
        story.append(RLImage(fig4_path, width=530, height=170))
        story.append(Paragraph(
            "Fig. 4. Comprehensive performance gains at 2000 GoCJ cloudlets: (a) Total Completion Time (TCT) reduction saving up to "
            "3.49 million task seconds; (b) Datacenter host SPECpower energy consumption.", CA))
    story.append(sp(2))

    story.append(Paragraph(
        "<i>Key Insight: When accounting for context-switching overhead (δ_cs = 5 ms), Classical RR suffers from hundreds of preemption "
        "penalties per task. In contrast, SSP-ARR's adaptive quantum consolidation reduces context switches by over 75%, yielding consistently "
        "shorter cluster makespans across all global policies (saving 22.6 s under PSSLB and 6.34 s under Dy. MM), translating directly "
        "into increased throughput and lower host energy consumption across all 30 datacenter hosts.</i>", IN))
    story.append(sp(3))

    story.append(Paragraph("E. Key Mechanisms Behind SSP-ARR Performance Gains", H2))
    story.append(Paragraph("The performance superiority of SSP-ARR stems from four foundational design principles:", BN))
    story.append(Paragraph("1. <b>Variance-Aware Stability Switching</b>: Classical RR treats all queues identically, while MAADRR applies median slicing regardless of variance. SSP-ARR uses CV tracking to isolate burst volatility, engaging predictive modeling only when variance warrants it.", BL))
    story.append(Paragraph("2. <b>Adaptive EWMA Quantum Tuning</b>: The error-driven learning rate &alpha; &isin; [0.20, 0.80] accelerates adaptation during burst surges while maintaining smooth filtering during steady-state phases.", BL))
    story.append(Paragraph("3. <b>Fail-Safe Confidence Gating</b>: Restricting EWMA usage to predictions with NPE &le; 20% guarantees that inaccurate forecasts never destabilize local VM queues.", BL))
    story.append(Paragraph("4. <b>Preemption Consolidation</b>: Sizing the quantum dynamically around true burst medians and forecasts enables cloudlets to complete in 1–3 slices rather than dozens of 1.0-second fragments, reclaiming wasted CPU cycles.", BL))

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 7: TWO-COLUMN (DISCUSSION, CONCLUSION, ACKNOWLEDGMENT, REFERENCES)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(NextPageTemplate('TwoCol'))
    story.append(PageBreak())

    story.append(Paragraph("VI. COMPARATIVE DISCUSSION", H1))
    story.append(Paragraph("A. Orthogonality to Global Schedulers", H2))
    story.append(Paragraph(
        "A critical finding of this study is the <b>architectural orthogonality</b> between Tier-1 global dispatchers and Tier-2 local schedulers. "
        "Regardless of whether the broker uses dynamic Max-Min heuristics, multi-resource indices (DRALBA), priority tiers (PSSLB/PSSELB), "
        "or dispersion thresholding (DeRALBA), <b>SSP-ARR reliably cuts AWT by ~50% and ATAT by 36% to 49%</b>. Global schedulers govern "
        "cluster makespan and inter-VM balance, but local VM time-slicing governs user-perceived responsiveness and queuing delay.", B))

    story.append(Paragraph("B. Threats to Validity", H2))
    story.append(Paragraph("1. <b>Simulation vs. Production Overheads</b>: Experiments were executed on CloudSim Plus 8.5.7. Hardware hypervisor cache effects (L1/L2 thrashing) in production KVM/Xen environments may introduce additional context costs that further favor SSP-ARR.", BL))
    story.append(Paragraph("2. <b>Workload Generality</b>: Although GoCJ traces represent real-world Google datacenter jobs, serverless micro-benchmarks or streaming pipelines may require tuning the stability window W.", BL))

    story.append(Paragraph("VII. CONCLUSION &amp; FUTURE WORK", H1))
    story.append(Paragraph(
        "In this paper, we presented <b>SSP-ARR</b> (<b>S</b>tability-<b>S</b>witched <b>P</b>redictive <b>A</b>daptive <b>R</b>ound <b>R</b>obin), "
        "an intelligent, multi-tier scheduling framework for heterogeneous cloud platforms. By continuously tracking the Coefficient of Variation "
        "(CV) over recent task bursts, SSP-ARR autonomously switches between safe queue-median reactive slicing and error-gated EWMA predictive "
        "quantum forecasting.", B))
    story.append(Paragraph(
        "Rigorously evaluated using CloudSim Plus 8.5.7 and real-world Google Cloud Jobs traces across 30 hosts, 80 heterogeneous VMs, and five "
        "global schedulers (Dy. MM, DRALBA, PSSLB, PSSELB, DeRALBA), SSP-ARR consistently reduced Average Waiting Time by <b>~50.2%</b>, "
        "reduced Average Turnaround Time by up to <b>49.2%</b>, and saved millions of cumulative completion seconds while maintaining superior "
        "throughput and host energy efficiency.", B))
    story.append(Paragraph(
        "Future work will explore extending SSP-ARR with Deep Q-Networks to dynamically tune stability threshold &theta;<sub>CV</sub> and "
        "integrating DVFS-aware host power consolidation.", B))

    story.append(Paragraph("ACKNOWLEDGMENT", ParagraphStyle('Ack', fontName='Times-Bold', fontSize=8, leading=10, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph("This research evaluation framework was developed for advanced cloud task scheduling research.", styles['caption']))

    # Move to Column 2 of Page 7 for References
    story.append(FrameBreak())

    story.append(Paragraph("REFERENCES", H1))
    for ref in REFS:
        story.append(Paragraph(ref, RF))

    return story


def create_pdf(output_path):
    print(f"Generating comprehensive IEEE PDF: {output_path}")
    styles = build_pdf_styles()
    story = build_pdf_story(styles)

    # 1. Header Frame on First Page (Title, 6 Author Slots)
    HEADER_H = 168.0
    BODY_H_P1 = PAGE_H - 2 * MARGIN_V - HEADER_H - 6.0

    f_top = Frame(
        MARGIN_H, PAGE_H - MARGIN_V - HEADER_H,
        FULL_W, HEADER_H,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='header_frame'
    )
    f_p1_c1 = Frame(
        MARGIN_H, MARGIN_V,
        COL_W, BODY_H_P1,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='p1_col1'
    )
    f_p1_c2 = Frame(
        MARGIN_H + COL_W + COL_GAP, MARGIN_V,
        COL_W, BODY_H_P1,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='p1_col2'
    )
    first_page_template = PageTemplate(
        id='FirstPage',
        frames=[f_top, f_p1_c1, f_p1_c2]
    )

    # 2. Standard Two-Column Template
    f_c1 = Frame(
        MARGIN_H, MARGIN_V,
        COL_W, PAGE_H - 2 * MARGIN_V,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='c1'
    )
    f_c2 = Frame(
        MARGIN_H + COL_W + COL_GAP, MARGIN_V,
        COL_W, PAGE_H - 2 * MARGIN_V,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='c2'
    )
    two_col_template = PageTemplate(
        id='TwoCol',
        frames=[f_c1, f_c2]
    )

    # 3. Full-Width Template for wide comparison tables
    f_full = Frame(
        MARGIN_H, MARGIN_V,
        FULL_W, PAGE_H - 2 * MARGIN_V,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='full'
    )
    full_width_template = PageTemplate(
        id='FullWidth',
        frames=[f_full]
    )

    doc = BaseDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=MARGIN_H,
        rightMargin=MARGIN_H,
        topMargin=MARGIN_V,
        bottomMargin=MARGIN_V,
    )
    doc.addPageTemplates([first_page_template, two_col_template, full_width_template])

    # After first page, standard text uses TwoCol
    story_with_transitions = story[:6] + [NextPageTemplate('TwoCol')] + story[6:]

    doc.build(story_with_transitions, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. PYTHON-DOCX GENERATION (OFFICIAL IEEE 2-COLUMN TEMPLATE FORMAT)
# ─────────────────────────────────────────────────────────────────────────────
def create_docx(docx_path):
    print(f"Generating official IEEE DOCX matching conference template: {docx_path}")
    doc = docx.Document()

    # SECTION 1: FULL-WIDTH HEADER (Page Setup & Margins)
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(0.625)
    sec1.right_margin = Inches(0.625)
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)

    # Style definitions
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(10)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.05
    style_normal.paragraph_format.space_after = Pt(3)

    def set_cell_background(cell, color_hex):
        shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

    def set_cell_margins(cell, top=40, bottom=40, left=60, right=60):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            m = OxmlElement(f'w:{margin_name}')
            m.set(qn('w:w'), str(val))
            m.set(qn('w:type'), 'dxa')
            tcMar.append(m)
        tcPr.append(tcMar)

    def format_table(table, col_widths=None):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            if i == 0:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            for j, cell in enumerate(row.cells):
                set_cell_margins(cell, top=35, bottom=35, left=50, right=50)
                if i == 0:
                    set_cell_background(cell, "D0D8E4")
                elif i % 2 == 1:
                    set_cell_background(cell, "F8F9FA")
                if col_widths and j < len(col_widths):
                    cell.width = Inches(col_widths[j])

    # Header catalog text
    p_cat = doc.add_paragraph()
    r_cat = p_cat.add_run("XXX-X-XXXX-XXXX-X/XX/$XX.00 ©20XX IEEE")
    r_cat.font.size = Pt(8)
    p_cat.paragraph_format.space_after = Pt(4)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(
        "SSP-ARR: Stability-Switched Predictive Adaptive Round Robin for Multi-Tier "
        "Cloud Task Scheduling Using Real-World Cloud Workload Traces"
    )
    r_title.bold = True
    r_title.font.size = Pt(20)
    p_title.paragraph_format.space_after = Pt(2)

    # Title Note
    p_tnote = doc.add_paragraph()
    p_tnote.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tnote = p_tnote.add_run("*Note: Sub-titles are not captured in Xplore and should not be used")
    r_tnote.italic = True
    r_tnote.font.size = Pt(8)
    p_tnote.paragraph_format.space_after = Pt(8)

    # 6 Author Slots in 3 Columns (matching IEEE template)
    t_auth = doc.add_table(rows=2, cols=3)
    t_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    auth_labels = [
        ("1st Given Name Surname", "2nd Given Name Surname", "3rd Given Name Surname"),
        ("4th Given Name Surname", "5th Given Name Surname", "6th Given Name Surname")
    ]
    for row_idx in range(2):
        for col_idx in range(3):
            cell = t_auth.rows[row_idx].cells[col_idx]
            cell.width = Inches(2.4)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            
            r1 = p.add_run(f"line 1: {auth_labels[row_idx][col_idx]}\n")
            r1.bold = True
            r1.font.size = Pt(8.5)
            r2 = p.add_run(
                "line 2: dept. name of organization\n(of Affiliation)\n"
                "line 3: name of organization (of Affiliation)\n"
                "line 4: City, Country\n"
                "line 5: email address or ORCID"
            )
            r2.font.size = Pt(7.5)
            r2.italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2: OFFICIAL IEEE TWO-COLUMN SECTION
    # ═══════════════════════════════════════════════════════════════════════════
    sec2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    cols2 = sec2._sectPr.xpath('./w:cols')
    if cols2:
        cols2[0].set(qn('w:num'), '2')
        cols2[0].set(qn('w:space'), '360')
    else:
        sec2._sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="360"/>'))

    # Helper functions
    def add_h1(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(10)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.italic = True
        r.font.size = Pt(9.5)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        return p

    def add_body(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.18)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.font.size = Pt(9.5)
        return p

    def add_eq(formula, num=""):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(formula)
        r.italic = True
        r.font.size = Pt(9)
        if num:
            r_num = p.add_run(f"    ({num})")
            r_num.bold = True
            r_num.italic = False
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        return p

    def add_caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(8.5)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(3)
        return p

    def add_table_head(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(8.5)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        return p

    # Abstract & Keywords (Column 1)
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_absh = p_abs.add_run("Abstract—")
    r_absh.bold = True
    r_absh.italic = True
    r_absh.font.size = Pt(9)
    r_abst = p_abs.add_run(
        "Task scheduling in heterogeneous cloud datacenters plays a decisive role in maximizing computational "
        "resource efficiency, reducing end-user latency, and lowering datacenter energy footprint. However, conventional time-sharing "
        "schedulers—predominantly Classical Round Robin (RR) and its static variants—rely on rigid, pre-configured CPU time quanta. "
        "Under burst-heavy, heterogeneous, and unpredictable cloud workloads, fixed time-slicing causes severe head-of-line blocking "
        "(the convoy effect), excessive context-switching overhead, and inflated waiting times. While reactive adaptive schedulers "
        "(such as MAADRR) compute median-based time quanta, purely reactive heuristics exhibit latency lag during sudden workload phase "
        "transitions and fail to anticipate high-variance task arrivals. To overcome these limitations, this paper proposes SSP-ARR "
        "(Stability-Switched Predictive Adaptive Round Robin), an intelligent, multi-tier scheduling framework tailored for heterogeneous "
        "cloud infrastructures. SSP-ARR dynamically evaluates workload volatility at the local VM tier using a sliding-window Coefficient "
        "of Variation (CV). When queue variance remains stable (CV ≤ 0.50), the scheduler operates in a safe queue-median reactive mode; "
        "when volatility surges (CV > 0.50), it transitions to an adaptive Exponentially Weighted Moving Average (EWMA) predictive mode "
        "governed by an error-modulated learning rate and strict confidence gating (Normalized Prediction Error ≤ 0.20). Furthermore, "
        "task queues are structured under Shortest Remaining Processing Time (SRPT) ordering with bounded quantum clamping [0.001 s, 60.0 s]. "
        "SSP-ARR is evaluated across five state-of-the-art global dispatching strategies (Dynamic Max-Min, DRALBA, PSSLB, PSSELB, and DeRALBA) "
        "using real-world Google Cloud Jobs (GoCJ) traces spanning 100 to 2000 cloudlets on CloudSim Plus 8.5.7. Experimental results "
        "demonstrate that SSP-ARR achieves an average reduction of ~50.2% in Average Waiting Time (AWT), up to 49.2% improvement in Average "
        "Turnaround Time (ATAT), saves millions of cumulative completion seconds in Total Completion Time (TCT), and yields superior makespan, "
        "throughput, and SPECpower-modeled energy efficiency compared to Classical RR across all global policies."
    )
    r_abst.bold = True
    r_abst.font.size = Pt(8.5)
    p_abs.paragraph_format.space_after = Pt(3)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kwh = p_kw.add_run("Keywords—")
    r_kwh.bold = True
    r_kwh.italic = True
    r_kwh.font.size = Pt(9)
    r_kwt = p_kw.add_run(
        "Cloud task scheduling, multi-tier architecture, adaptive dynamic time quantum, stability switching, "
        "coefficient of variation, EWMA prediction, GoCJ workload traces, CloudSim Plus."
    )
    r_kwt.font.size = Pt(8.5)
    p_kw.paragraph_format.space_after = Pt(8)

    # ── SECTION I ──
    add_h1("I. INTRODUCTION")
    add_body(
        "Cloud computing platforms have emerged as the foundational utility for modern enterprise IT, scientific computing, "
        "and consumer applications [1], [2]. The elastic resource model allows providers to multiplex massive pools of virtualized "
        "compute, memory, and network resources among thousands of concurrently competing client workloads [3], [4]. In this environment, "
        "task scheduling is decisive in determining whether a cloud provider can satisfy Service Level Agreements (SLAs), minimize operating "
        "costs, and prevent severe server thermal dissipation [5], [6]."
    )
    add_body(
        "Task scheduling in cloud computing typically operates across a two-tier hierarchy [7], [8]. At the first tier, global broker "
        "schedulers receive incoming user tasks and map them to appropriate Virtual Machines (VMs) across distributed datacenters [9]. At the "
        "second tier, local VM hypervisor schedulers manage the execution sequence of cloudlets residing in each VM's circular ready queue [10]. "
        "While substantial research has focused on global heuristic and metaheuristic dispatchers, the efficiency of local VM scheduling "
        "remains the critical determinant of actual CPU core utilization, context-switching overhead, and task waiting times [11], [12]."
    )
    add_body(
        "At the local VM level, Classical Round Robin (RR) has historically been the default choice due to its simplicity, starvation prevention, "
        "and conceptual fairness [13], [14]. However, Classical RR is burdened by a critical architectural limitation: reliance on a static, "
        "pre-configured Time Quantum (TQ). If the quantum is set too small, the system suffers severe throughput degradation from frequent "
        "CPU context switches [15]. Conversely, if the quantum is set too large, Classical RR degenerates into First-Come First-Served (FCFS), "
        "causing short tasks to stall behind long, compute-heavy jobs—an anomaly known as the convoy effect [16]."
    )
    add_body(
        "Recent advances have attempted to mitigate this trade-off by introducing dynamic time quantum adaptation, such as the Multi-Agent "
        "Adaptive Dynamic Round Robin (MAADRR) scheduler [16]. MAADRR dynamically computes the time quantum as the median of task burst lengths "
        "in the VM queue. While MAADRR improves upon static RR under moderate conditions, its purely reactive formulation exhibits severe latency "
        "lag during rapid workload phase changes and fails to anticipate task burst variance under volatile real-world traffic."
    )
    add_body(
        "To resolve these challenges, this paper presents SSP-ARR (Stability-Switched Predictive Adaptive Round Robin), an intelligent local VM "
        "scheduling framework that incorporates continuous variance sensing, dual-mode reactive/predictive quantum selection, confidence gating, "
        "and bounded preemption clamping within a multi-tier cloud hierarchy."
    )

    # ── SECTION II ──
    add_h1("II. RELATED WORK & ARCHITECTURAL EVOLUTION")
    add_h2("A. Adaptive Round Robin Variants")
    add_body(
        "Dynamic time quantum adaptation has received extensive research interest. In [17], the authors proposed a hybrid Min-Min and Round "
        "Robin algorithm to combine the makespan minimization of Min-Min with the fairness of Round Robin. Runsungnoen and Anusas-Amornkul [18] "
        "developed the RR_RT&M technique, utilizing remaining task execution time and median estimation to adapt the quantum. Ghazy et al. [19] "
        "formulated an ameliorated Round Robin algorithm calculating quantum based on arithmetic mean of remaining bursts. Similarly, Banerjee "
        "et al. [20] presented Optimized Round Robin (ORR), proving that dynamic time quantum selection significantly mitigates average waiting "
        "time and turnaround time compared to static baselines. Mazumder et al. [21] introduced Priority-based Round Robin (PRR) prioritizing "
        "tasks according to burst length and deadline thresholds."
    )
    add_h2("B. Multi-Tier Global Schedulers")
    add_body(
        "Global schedulers govern the distribution of cloudlets across heterogeneous VMs. Five representative global dispatching strategies "
        "are considered in this investigation: (1) Dynamic Max-Min (Dy. MM) [17], which dynamically maps large tasks to fast VMs while "
        "recomputing completion times to prevent small task starvation; (2) DRALBA [22], a dynamic and resource-aware load-balancing "
        "algorithm utilizing multi-resource variance minimization; (3) PSSLB [23], a priority-based queue-state scheduling algorithm; "
        "(4) PSSELB [23], an enhanced energy-aware variant of PSSLB; and (5) DeRALBA [24], which integrates dispersion thresholding "
        "with adaptive candidate matching."
    )
    add_h2("C. Evolution to SSP-ARR")
    add_body(
        "Existing local schedulers fall into two flawed extremes: static allocation (RR) or unconstrained reactive heuristics (MAADRR). "
        "Neither architecture explicitly measures queue burst variance or employs predictive models to anticipate burst length trends. "
        "Table I highlights the evolutionary architectural progression from Classical RR and MAADRR to SSP-ARR."
    )

    # Table I
    add_table_head("TABLE I. ARCHITECTURAL COMPARISON ACROSS CLOUD LOCAL SCHEDULING MODELS")
    t1_docx = doc.add_table(rows=1, cols=4)
    hdr1 = t1_docx.rows[0].cells
    hdr1[0].text = "Feature"
    hdr1[1].text = "Classical RR"
    hdr1[2].text = "MAADRR [16]"
    hdr1[3].text = "Proposed SSP-ARR"
    for r in [
        ("Quantum Sizing", "Static (1.0 s)", "Dynamic Median", "Dual Reactive / Predictive Mode"),
        ("Workload Sensing", "None", "Reactive only", "CV Stability Sensing (θ_CV = 0.50)"),
        ("Burst Prediction", "None", "None", "Adaptive EWMA (α ∈ [0.20, 0.80])"),
        ("Confidence Gating", "None", "None", "NPE ≤ 0.20 Strict Gating"),
        ("Queue Ordering", "FIFO", "FIFO / Re-sort", "SRPT Ascending Order"),
        ("Quantum Clamping", "Fixed", "Unbounded", "Bounded Clamping [0.001s, 60.0s]"),
        ("Preemption Penalty", "High (Severe)", "Moderate", "Minimal (Consolidated Execution)"),
        ("Global Tier Support", "Single-tier", "Multi-agent", "5 Global Dispatchers Supported"),
    ]:
        row = t1_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t1_docx, col_widths=[0.9, 0.75, 0.85, 1.0])

    # ── SECTION III ──
    add_h1("III. MATHEMATICAL DESIGN AND ALGORITHMIC FORMULATION")
    add_h2("A. Multi-Tier System Architecture")
    add_body(
        "The proposed architecture operates across two coordinated tiers: (1) Tier-1 Global Datacenter Dispatching assigns "
        "submitted cloudlets to VMs using established global balancing policies; (2) Tier-2 Local VM Scheduling governs cloudlet "
        "preemption and execution via SSP-ARR, depicted in Fig. 1."
    )

    # Embed Figure 1 in Word
    fig1_path = os.path.join(FIGURES_DIR, "fig1_architecture.png")
    if os.path.exists(fig1_path):
        doc.add_paragraph().paragraph_format.space_before = Pt(2)
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.add_run().add_picture(fig1_path, width=Inches(3.3))
        add_caption("Fig. 1. Architectural workflow of the proposed SSP-ARR multi-tier framework.")

    add_h2("B. Workload Volatility Sensing via CV")
    add_body(
        "For each VM v_j, let H_j = {B_{j,1}, ..., B_{j,W}} represent execution bursts of the last W completed cloudlets (W = 5). "
        "The local agent tracks sample mean μ_j and sample standard deviation σ_j:", indent=False
    )
    add_eq("μ_j = (1/W) · Σ B_{j,k}", "1")
    add_eq("σ_j = √[ (1/W) · Σ (B_{j,k} − μ_j)² ]", "2")
    add_body("The Coefficient of Variation (CV_j) is defined as:", indent=False)
    add_eq("CV_j = σ_j / μ_j", "3")
    add_body("• Stable Regime (CV_j ≤ θ_CV): Low dispersion (θ_CV = 0.50). Safe Reactive Mode selected.", indent=False)
    add_body("• Volatile Regime (CV_j > θ_CV): High burst variability. Predictive EWMA Mode activated.", indent=False)

    add_h2("C. Dual-Mode Quantum Allocation Engine")
    add_body("1) Safe Reactive Mode (CV_j ≤ θ_CV): Quantum computed as queue median:", indent=False)
    add_eq("Q_reactive = median( {RB(x) : x ∈ Q_j} ∪ {RB(t)} )", "4")
    add_body("2) Predictive EWMA Mode (CV_j > θ_CV): Optimal burst duration forecasted by EWMA:", indent=False)
    add_eq("B_pred_{j,t+1} = α_t · B_{j,t} + (1 − α_t) · B_pred_{j,t}", "5")
    add_body("where α_t is an adaptive error-modulated learning rate:", indent=False)
    add_eq("α_t = 0.20 if NPE < 0.10  |  0.40 if 0.10 ≤ NPE < 0.20", "6a")
    add_eq("α_t = 0.60 if 0.20 ≤ NPE < 0.30  |  0.80 if NPE ≥ 0.30", "6b")
    add_body("3) Normalized Prediction Error (NPE) and Confidence Gating:", indent=False)
    add_eq("NPE_t = |B_{j,t} − B_pred_{j,t}| / B_{j,t}", "7")
    add_body("Predictions are gated by confidence threshold τ_gate = 0.20:", indent=False)
    add_eq("Q_selected = B_pred_{j,t+1}  if (CV_j > 0.50 and NPE_t ≤ 0.20)", "8a")
    add_eq("Q_selected = Q_reactive   otherwise (fallback to median)", "8b")
    add_body("4) Boundary Clamping: Clamped within [0.001 s, 60.0 s]:", indent=False)
    add_eq("Q_j = max(Q_min, min(Q_max, min(Q_selected, RB(t))))", "9")

    # Algorithm 1 Box
    add_h2("D. Formal Algorithmic Pseudocode")
    add_caption("Algorithm 1: Multi-Tier Cloud Task Scheduling with SSP-ARR")
    t_algo = doc.add_table(rows=1, cols=1)
    cell_algo = t_algo.rows[0].cells[0]
    set_cell_background(cell_algo, "F4F6F9")
    set_cell_margins(cell_algo, top=60, bottom=60, left=80, right=80)
    p_code = cell_algo.paragraphs[0]
    p_code.paragraph_format.line_spacing = 1.0
    r_code = p_code.add_run(
        "Input : Cloudlet set C={c_1..c_n}; VM pool V={v_1..v_m};\n"
        "        Policy P in {Dy.MM, DRALBA, PSSLB, PSSELB, DeRALBA};\n"
        "        Q_min=0.001s, Q_max=60.0s; δ_cs=0.005s; θ_CV=0.50; τ_gate=0.20.\n"
        "// TIER 1: Global Datacenter Dispatching\n"
        "1: Assignment[] ← GlobalSchedulers.assign(P, C, V);\n"
        "2: Enqueue tasks to VM ready queues Q_1..Q_m;\n"
        "// TIER 2: Local SSP-ARR Execution per VM\n"
        "3: for each VM v_j with queue Q_j do\n"
        "4:   Sort Q_j in ascending order of burst (SRPT order);\n"
        "5:   while Q_j is not empty do\n"
        "6:     t ← Q_j.pollHead();\n"
        "7:     q_med ← median(Q_j, t);  cv ← ComputeCV(history);\n"
        "8:     if cv > θ_CV and npe ≤ τ_gate then q ← ewma;\n"
        "9:     else q ← q_med; end if\n"
        "10:    slice ← min(max(Q_min, min(Q_max, q)), t.remainingBurst);\n"
        "11:    t.remainingBurst -= slice; currentTime += slice;\n"
        "12:    if t.remainingBurst ≤ 1e-9 then\n"
        "13:      RecordCompletionStats(t); UpdateEWMA(t.burst);\n"
        "14:    else\n"
        "15:      currentTime += δ_cs; InsertSorted(Q_j, t);\n"
        "16:    end if\n"
        "17:  end while\n"
        "18: end for"
    )
    r_code.font.name = 'Consolas'
    r_code.font.size = Pt(7.5)
    format_table(t_algo, col_widths=[3.5])

    # Table II: Symbols
    add_h2("E. Table of Symbols and Notations")
    add_table_head("TABLE II. MATHEMATICAL SYMBOLS AND NOTATIONS")
    t2_docx = doc.add_table(rows=1, cols=2)
    hdr2 = t2_docx.rows[0].cells
    hdr2[0].text = "Symbol"
    hdr2[1].text = "Definition"
    for s, d in [
        ("VM_j, Q_j", "j-th Virtual Machine and its circular ready queue"),
        ("c_i, L_i", "i-th cloudlet and instruction length (in Million Instructions, MI)"),
        ("MIPS_j, RB", "Processing speed of VM_j and remaining burst duration (in seconds)"),
        ("CV_j, θ_CV", "Coefficient of Variation of bursts and stability threshold (0.50)"),
        ("B_pred, α_t", "EWMA-predicted burst duration and adaptive learning rate [0.20, 0.80]"),
        ("NPE, τ_gate", "Normalized Prediction Error and confidence gating threshold (0.20)"),
        ("Q_min, Q_max", "Bounded limits for time quantum allocation (0.001 s and 60.0 s)"),
        ("δ_cs", "Context switching and preemption penalty (δ_cs = 0.005 s / 5 ms)"),
        ("T_i, A_i, B_i", "Completion time, arrival time, and execution burst time of task i"),
        ("P_idle, P_max", "Idle and peak power consumption per host (150 W and 250 W)"),
    ]:
        r = t2_docx.add_row().cells
        r[0].text = s
        r[1].text = d
    format_table(t2_docx, col_widths=[1.0, 2.5])

    # ── SECTION IV ──
    add_h1("IV. EXPERIMENTAL SETUP & PERFORMANCE EVALUATION")
    add_h2("A. Cloud Simulation Environment")
    add_body(
        "The experimental framework is implemented using the CloudSim Plus 8.5.7 discrete-event cloud simulator on Java 21. "
        "CloudSim Plus provides fully extensible abstractions for datacenter brokers, host power profiles, and VM time-shared schedulers."
    )
    add_h2("B. Infrastructure & Heterogeneous VM Specifications")
    add_body(
        "The physical datacenter comprises 30 physical hosts (120 PEs total, 4 PEs/host @ 4000 MIPS each), 32 GB RAM, 100 Gbps network, "
        "and 1 TB storage. Host power consumption follows the linear SPECpower standard server model:"
    )
    add_eq("P_host(u) = P_idle + (P_max − P_idle) · u", "10")
    add_body(
        "where P_idle = 150 W, P_max = 250 W, and u ∈ [0, 1] is CPU utilization fraction. A pool of 80 heterogeneous VMs is instantiated "
        "with processing speeds ranging from 1000 to 4000 MIPS (step 200 MIPS)."
    )
    add_h2("C. Benchmark Workload: Google Cloud Jobs (GoCJ)")
    add_body(
        "The framework is evaluated using real-world Google-Cluster-like Job (GoCJ) traces [25], exhibiting realistic arrival bursts, "
        "asymmetric lengths, and high variance (CV ≈ 1.24). Evaluations span 12 workload scales: 100 to 2000 cloudlets (15,000–900,000 MI)."
    )

    # Table III
    add_table_head("TABLE III. SIMULATION ENVIRONMENT PARAMETERS SUMMARY")
    t3_docx = doc.add_table(rows=1, cols=2)
    hdr3 = t3_docx.rows[0].cells
    hdr3[0].text = "Parameter"
    hdr3[1].text = "Configuration Value"
    for p, v in [
        ("Simulation Engine", "CloudSim Plus 8.5.7 (Java 21)"),
        ("Physical Datacenter", "30 Hosts (120 PEs total, 4 PEs/Host @ 4000 MIPS)"),
        ("Host Power Profile", "SPECpower Linear Model (P_idle = 150 W, P_max = 250 W)"),
        ("Virtual Machines (VMs)", "80 Heterogeneous VMs (1000–4000 MIPS)"),
        ("VM Memory / BW", "8192 MB RAM, 20,000 Mbps Bandwidth"),
        ("Workload Benchmark", "Real-world Google Cloud Jobs (GoCJ)"),
        ("Workload Sizes", "100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000 tasks"),
        ("Global Schedulers (Tier 1)", "Dynamic Max-Min, DRALBA, PSSLB, PSSELB, DeRALBA"),
        ("Local Schedulers (Tier 2)", "Classical Round Robin (Fixed q = 1.0 s, FIFO) vs. SSP-ARR"),
        ("Context Switch Overhead", "δ_cs = 0.005 s (5 ms) per preemption"),
        ("Evaluation Runs", "3 independent runs per workload size (mean reported)"),
    ]:
        r = t3_docx.add_row().cells
        r[0].text = p
        r[1].text = v
    format_table(t3_docx, col_widths=[1.2, 2.3])

    add_h2("D. Performance Metrics")
    add_body("Evaluated using seven standard performance metrics:", indent=False)
    add_body("1. Average Waiting Time (AWT):", indent=False)
    add_eq("AWT = (1/N) · Σ (T_i − A_i − B_i)", "11")
    add_body("2. Average Turnaround Time (ATAT):", indent=False)
    add_eq("ATAT = (1/N) · Σ (T_i − A_i)", "12")
    add_body("3. Average Completion Time (ACT): Mean end-to-end task completion duration.", indent=False)
    add_body("4. Total Completion Time (TCT):", indent=False)
    add_eq("TCT = Σ T_i = N × ACT", "13")
    add_body("5. System Throughput (Thp):", indent=False)
    add_eq("Throughput = N / Makespan  (tasks/second)", "14")
    add_body("6. Host Energy Consumption (E_total):", indent=False)
    add_eq("E_total = (1/3,600,000) · Σ ∫P_j(t) dt  (kWh)", "15")
    add_body("7. Makespan (T_max): Total cluster finish time (max_i T_i).", indent=False)
    add_eq("Improvement_lower-better (%) = (X_RR − X_SSP) / X_RR × 100", "16")
    add_eq("Improvement_higher-better (%) = (X_SSP − X_RR) / X_RR × 100", "17")

    # ── SECTION V ──
    add_h1("V. RESULTS AND COMPARATIVE PERFORMANCE ANALYSIS")
    add_h2("A. Average Waiting Time (AWT)")
    add_body(
        "Average Waiting Time directly reflects queue congestion and the elimination of the convoy effect. "
        "Table IV presents the raw AWT values (in milliseconds) and Table V presents percentage improvements of SSP-ARR over Classical RR "
        "across all five global scheduling strategies."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3: FULL WIDTH FOR WIDE TABLES AND FIGURES (TABLE IV, FIG 2, TABLE V)
    # ═══════════════════════════════════════════════════════════════════════════
    sec_wide1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    cols_w1 = sec_wide1._sectPr.xpath('./w:cols')
    if cols_w1:
        cols_w1[0].set(qn('w:num'), '1')
    else:
        sec_wide1._sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="1"/>'))

    # Table IV in docx (Full Width = 7.25 in)
    add_table_head("TABLE IV. COMPARISON OF AWT (MS) FOR RR AND SSP-ARR (100–2000 GOCJ CLOUDLETS)")
    t4_docx = doc.add_table(rows=1, cols=11)
    for idx, h in enumerate(AWT_HDR):
        t4_docx.rows[0].cells[idx].text = h
    for r in AWT_ROWS:
        row = t4_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t4_docx, col_widths=[0.6] + [0.665]*10)

    # Embed Figure 2 across full width
    fig2_path = os.path.join(FIGURES_DIR, "fig2_awt_comparison.png")
    if os.path.exists(fig2_path):
        doc.add_paragraph().paragraph_format.space_before = Pt(4)
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(fig2_path, width=Inches(6.8))
        add_caption("Fig. 2. Average Waiting Time (AWT) comparison between Classical RR and SSP-ARR across five global scheduling strategies.")

    # Table V in docx
    add_table_head("TABLE V. PERCENTAGE IMPROVEMENT IN AWT (SSP-ARR OVER CLASSICAL RR)")
    t5_imp_docx = doc.add_table(rows=1, cols=6)
    for idx, h in enumerate(AWT_IMP_HDR):
        t5_imp_docx.rows[0].cells[idx].text = h
    for r in AWT_IMP_ROWS:
        row = t5_imp_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t5_imp_docx, col_widths=[1.2]*6)

    # Table VI in docx
    add_table_head("TABLE VI. COMPARISON OF ATAT (S) FOR RR AND SSP-ARR ACROSS FIVE GLOBAL SCHEDULERS")
    t6_docx = doc.add_table(rows=1, cols=11)
    for idx, h in enumerate(ATAT_HDR):
        t6_docx.rows[0].cells[idx].text = h
    for r in ATAT_ROWS:
        row = t6_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t6_docx, col_widths=[0.6] + [0.665]*10)

    # Embed Figure 3 across full width
    fig3_path = os.path.join(FIGURES_DIR, "fig3_atat_comparison.png")
    if os.path.exists(fig3_path):
        doc.add_paragraph().paragraph_format.space_before = Pt(4)
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.add_run().add_picture(fig3_path, width=Inches(6.8))
        add_caption("Fig. 3. Average Turnaround Time (ATAT) performance: (a) Absolute ATAT; (b) Load-proportional percentage improvement scaling.")

    # Table VII in docx
    add_table_head("TABLE VII. PERCENTAGE IMPROVEMENT IN ATAT (SSP-ARR OVER CLASSICAL RR)")
    t7_imp_docx = doc.add_table(rows=1, cols=6)
    for idx, h in enumerate(ATAT_IMP_HDR):
        t7_imp_docx.rows[0].cells[idx].text = h
    for r in ATAT_IMP_ROWS:
        row = t7_imp_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t7_imp_docx, col_widths=[1.2]*6)

    # Table VIII in docx
    add_table_head("TABLE VIII. COMPARISON OF TCT (SECONDS) FOR RR AND SSP-ARR ACROSS FIVE GLOBAL SCHEDULERS")
    t8_docx = doc.add_table(rows=1, cols=11)
    for idx, h in enumerate(TCT_HDR):
        t8_docx.rows[0].cells[idx].text = h
    for r in TCT_ROWS:
        row = t8_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t8_docx, col_widths=[0.6] + [0.665]*10)

    # Table IX in docx
    add_table_head("TABLE IX. PERFORMANCE SUMMARY OF MAKESPAN, THROUGHPUT, AND ENERGY AT 2000 GOCJ CLOUDLETS")
    t9_docx = doc.add_table(rows=1, cols=7)
    for idx, val in enumerate(TBL7_HDR):
        t9_docx.rows[0].cells[idx].text = val
    for r in TBL7_ROWS:
        row = t9_docx.add_row().cells
        for idx, val in enumerate(r):
            row[idx].text = val
    format_table(t9_docx, col_widths=[1.5, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95])

    # Embed Figure 4 across full width
    fig4_path = os.path.join(FIGURES_DIR, "fig4_tct_and_cluster.png")
    if os.path.exists(fig4_path):
        doc.add_paragraph().paragraph_format.space_before = Pt(4)
        p_img4 = doc.add_paragraph()
        p_img4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img4.add_run().add_picture(fig4_path, width=Inches(6.8))
        add_caption("Fig. 4. Comprehensive performance gains at 2000 GoCJ cloudlets: (a) TCT reduction saving up to 3.49M task seconds; (b) Datacenter host energy consumption.")

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4: RESUME TWO-COLUMN FOR DISCUSSION, CONCLUSION & REFERENCES
    # ═══════════════════════════════════════════════════════════════════════════
    sec_col2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    cols_c2 = sec_col2._sectPr.xpath('./w:cols')
    if cols_c2:
        cols_c2[0].set(qn('w:num'), '2')
        cols_c2[0].set(qn('w:space'), '360')
    else:
        sec_col2._sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="360"/>'))

    add_h2("E. Key Mechanisms Behind SSP-ARR Performance Gains")
    add_body("The performance superiority of SSP-ARR stems from four foundational design principles:", indent=False)
    add_body("1. Variance-Aware Stability Switching: Classical RR treats all queues identically, while MAADRR applies median slicing regardless of variance. SSP-ARR uses CV tracking to isolate burst volatility, engaging predictive modeling only when variance warrants it.", indent=False)
    add_body("2. Adaptive EWMA Quantum Tuning: The error-driven learning rate α ∈ [0.20, 0.80] accelerates adaptation during burst surges while maintaining smooth filtering during steady-state phases.", indent=False)
    add_body("3. Fail-Safe Confidence Gating: Restricting EWMA usage to predictions with NPE ≤ 20% guarantees that inaccurate forecasts never destabilize local VM queues.", indent=False)
    add_body("4. Preemption Consolidation: Sizing the quantum dynamically around true burst medians and forecasts enables cloudlets to complete in 1 to 3 slices rather than dozens of 1.0-second fragments, reclaiming wasted CPU cycles.", indent=False)

    add_h1("VI. COMPARATIVE DISCUSSION")
    add_h2("A. Orthogonality to Global Schedulers")
    add_body(
        "A critical finding of this study is the architectural orthogonality between Tier-1 global dispatchers and Tier-2 local schedulers. "
        "Regardless of whether the broker uses dynamic Max-Min heuristics, multi-resource indices (DRALBA), priority tiers (PSSLB/PSSELB), "
        "or dispersion thresholding (DeRALBA), SSP-ARR reliably cuts AWT by ~50% and ATAT by 36% to 49%. Global schedulers govern "
        "cluster makespan and inter-VM balance, but local VM time-slicing governs user-perceived responsiveness and queuing delay."
    )
    add_h2("B. Threats to Validity")
    add_body(
        "1. Simulation vs. Production Overheads: Experiments were executed on CloudSim Plus 8.5.7. Hardware hypervisor cache effects "
        "(L1/L2 thrashing) in production KVM/Xen environments may introduce additional context costs that further favor SSP-ARR."
    )
    add_body(
        "2. Workload Generality: Although GoCJ traces represent real-world Google datacenter jobs, serverless micro-benchmarks or long-running "
        "streaming pipelines may require tuning the stability window W."
    )

    add_h1("VII. CONCLUSION & FUTURE WORK")
    add_body(
        "In this paper, we presented SSP-ARR (Stability-Switched Predictive Adaptive Round Robin), an intelligent, multi-tier scheduling "
        "framework for heterogeneous cloud platforms. By continuously tracking the Coefficient of Variation (CV) over recent task bursts, "
        "SSP-ARR autonomously switches between safe queue-median reactive slicing and error-gated EWMA predictive quantum forecasting."
    )
    add_body(
        "Rigorously evaluated using CloudSim Plus 8.5.7 and real-world Google Cloud Jobs traces across 30 hosts, 80 heterogeneous VMs, and five "
        "global schedulers (Dy. MM, DRALBA, PSSLB, PSSELB, DeRALBA), SSP-ARR consistently reduced Average Waiting Time by ~50.2%, "
        "reduced Average Turnaround Time by up to 49.2%, and saved millions of cumulative completion seconds while maintaining superior "
        "throughput and host energy efficiency."
    )
    add_body(
        "Future work will explore extending SSP-ARR with reinforcement learning agents (Deep Q-Networks) to dynamically tune the stability "
        "threshold θ_CV and integrating DVFS-aware host power consolidation to shut down idle VMs during low-traffic periods."
    )

    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ack = p_ack.add_run("ACKNOWLEDGMENT")
    r_ack.bold = True
    r_ack.font.size = Pt(9)
    p_ack.paragraph_format.space_before = Pt(8)
    p_ack.paragraph_format.space_after = Pt(2)
    add_body("This template and research evaluation framework was developed for advanced cloud task scheduling research.", indent=False)

    add_h1("REFERENCES")
    for r in REFS:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.25)
        p_ref.paragraph_format.first_line_indent = Inches(-0.25)
        p_ref.paragraph_format.space_after = Pt(2)
        r_run = p_ref.add_run(r)
        r_run.font.size = Pt(8)

    doc.save(docx_path)
    print(f"DOCX successfully generated: {docx_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. SCRIPT ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # First generate all figures if they don't exist
    import generate_paper_assets
    generate_paper_assets.create_fig1_architecture()
    generate_paper_assets.create_fig2_awt()
    generate_paper_assets.create_fig3_atat()
    generate_paper_assets.create_fig4_tct_and_cluster()

    pdf_out = os.path.join(BASE_DIR, "SSP_ARR_Research_Paper.pdf")
    docx_out = os.path.join(BASE_DIR, "SSP_ARR_Research_Paper.docx")

    create_pdf(pdf_out)
    create_docx(docx_out)
    print("ALL IEEE DOCUMENTS SUCCESSFULLY CREATED!")
