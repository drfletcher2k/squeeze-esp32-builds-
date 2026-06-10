#!/usr/bin/env python3
"""
Wiring diagram generator: 2x Freenove ESP32-S3 CAM + 2x PCM5102A DAC
Squeezelite-ESP32 dual player setup
"""

import sys

lines = []
def o(s): lines.append(s)

W, H = 1800, 4600

# ── color palette ──────────────────────────────────────────────────────────────
C = {
    "bg":       "#F8F7F2",
    "bb":       "#D8CFBE",       # breadboard body
    "bb_s":     "#B0A898",       # breadboard stroke
    "rail_r":   "#FFCCCC",       # red rail bg
    "rail_b":   "#CCDEFF",       # blue rail bg
    "hole":     "#BBBBBB",
    "hole_s":   "#888888",
    "hole_u":   "#505050",       # used hole
    "esp_pcb":  "#1A237E",       # ESP32 PCB dark blue
    "dac_pcb":  "#1B5E20",       # DAC PCB dark green
    "white":    "#FFFFFF",
    "hdr":      "#0D47A1",       # section headers
    "hdr_t":    "#E3F2FD",
    "title_bg": "#1A237E",
    "table_h":  "#37474F",
    "table_r1": "#ECEFF1",
    "table_r2": "#CFD8DC",
    # wire colours
    "w_3v3":    "#CC0000",
    "w_gnd":    "#111111",
    "w_bclk":   "#E65100",
    "w_ws":     "#6A1B9A",
    "w_dout":   "#1B5E20",
    "w_sck":    "#01579B",
    "w_fmt":    "#4E342E",
    "w_xmt":    "#880E4F",
}

# ── helpers ────────────────────────────────────────────────────────────────────
def rect(x,y,w,h,fill,stroke="none",sw=1,rx=0):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
    if stroke!="none": s+=f' stroke="{stroke}" stroke-width="{sw}"'
    if rx: s+=f' rx="{rx}"'
    o(s+'/>')

def txt(x,y,t,sz=13,fill="#000",anchor="middle",bold=False,italic=False,ff="Arial,sans-serif"):
    fw = "bold" if bold else "normal"
    fs = "italic" if italic else "normal"
    o(f'<text x="{x}" y="{y}" font-size="{sz}" fill="{fill}" text-anchor="{anchor}" '
      f'font-family="{ff}" font-weight="{fw}" font-style="{fs}">{t}</text>')

def ln(x1,y1,x2,y2,stroke,sw=2,dash="",cap="round"):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"'
    if dash: s+=f' stroke-dasharray="{dash}"'
    o(s+'/>')

def circ(cx,cy,r,fill,stroke="none",sw=1):
    s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
    if stroke!="none": s+=f' stroke="{stroke}" stroke-width="{sw}"'
    o(s+'/>')

def poly(pts,stroke,sw=2,fill="none",dash=""):
    ps = " ".join(f"{x},{y}" for x,y in pts)
    s = f'<polyline points="{ps}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round"'
    if dash: s+=f' stroke-dasharray="{dash}"'
    o(s+'/>')

def label_pill(x,y,text_str,bg,fg,w=90,h=16,sz=9):
    rect(x-w//2,y-h//2,w,h,bg,stroke=fg,sw=0.5,rx=4)
    txt(x,y+4,text_str,sz=sz,fill=fg,anchor="middle",bold=True)

def section_header(y, title):
    rect(0,y,W,30,C["hdr"])
    txt(W//2,y+20,f"▶  {title}",sz=16,fill=C["hdr_t"],bold=True)

# ── SVG open ───────────────────────────────────────────────────────────────────
o('<?xml version="1.0" encoding="UTF-8"?>')
o(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
o('<defs>')
o('<marker id="ah" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">')
o('<polygon points="0 0, 8 3, 0 6" fill="#555"/>')
o('</marker>')
o('</defs>')
rect(0,0,W,H,C["bg"])

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════════
rect(0,0,W,100,C["title_bg"])
rect(0,0,W,4,"#FF6F00")  # orange accent
txt(W//2,35,"ESP32-S3 CAM + PCM5102A   |   Squeezelite Dual Player Wiring",
    sz=24,fill="#FFFFFF",bold=True)
txt(W//2,58,"Freenove ESP32-S3 CAM (×2)  +  Teyleten PCM5102A I²S DAC (×2)  on 400-tie Breadboards",
    sz=14,fill="#90CAF9")
txt(W//2,78,"I²S: BCLK=GPIO40  WS=GPIO41  DOUT=GPIO42  |  DAC power: 3.3 V  |  SCK tied to GND (internal PLL)",
    sz=11,fill="#BBDEFB")
rect(0,96,W,4,"#FF6F00")

# ═══════════════════════════════════════════════════════════════════════════════
# BREADBOARD DIAGRAMS
# ═══════════════════════════════════════════════════════════════════════════════
section_header(102, "BREADBOARD WIRING DIAGRAMS  (top view — identical for both players)")

# ── Breadboard parameters ──────────────────────────────────────────────────────
HP = 17   # hole pitch px
NR = 30   # rows

# Column x-offsets within breadboard (relative to bb left edge)
ML = 24           # left margin
NEG_L  = ML            # neg rail col centre
POS_L  = ML+HP         # pos rail col centre
RAIL_GAP = 8
COL_A  = POS_L+HP+RAIL_GAP          # col a
# b,c,d,e
CENTER_GAP = 14
COL_F  = COL_A+5*HP+CENTER_GAP      # col f
# g,h,i,j
POS_R  = COL_F+5*HP+RAIL_GAP        # pos right rail
NEG_R  = POS_R+HP                   # neg right rail
MR = 24           # right margin

BB_W = NEG_R+HP+MR    # total breadboard width
BB_H = NR*HP+60       # top label + rows + bottom label

# Vertical: first row y within breadboard
ROW_TOP = 42

# two boards side by side
BB_Y   = 145
BB1_X  = 30
BB2_X  = BB1_X + BB_W + 80
PLAYER_LABEL_Y = BB_Y - 12

def col_x(bb_x, col_name):
    offsets = {
        'a': COL_A,'b':COL_A+HP,'c':COL_A+2*HP,'d':COL_A+3*HP,'e':COL_A+4*HP,
        'f':COL_F,'g':COL_F+HP,'h':COL_F+2*HP,'i':COL_F+3*HP,'j':COL_F+4*HP,
    }
    return bb_x + offsets[col_name] + HP//2

def row_y(bb_y, row):  # row 1..30
    return bb_y + ROW_TOP + (row-1)*HP + HP//2

def rail_x(bb_x, side, pol):
    if side=='L':
        return bb_x + (POS_L if pol=='+' else NEG_L) + HP//2
    else:
        return bb_x + (POS_R if pol=='+' else NEG_R) + HP//2

def draw_breadboard(bbx, bby, player_label):
    """Draw bare breadboard"""
    # Body
    rect(bbx, bby, BB_W, BB_H, C["bb"], C["bb_s"], 1.5, rx=5)

    # Rail strips
    rect(bbx+ML-3,         bby+ROW_TOP-6, HP*2+6, NR*HP+12, C["rail_r"], "none", 0, rx=3)
    rect(bbx+POS_R-3,      bby+ROW_TOP-6, HP*2+6, NR*HP+12, C["rail_b"], "none", 0, rx=3)

    # Column headers (top & bottom)
    for cn,base in [('a',COL_A),('b',COL_A+HP),('c',COL_A+2*HP),('d',COL_A+3*HP),('e',COL_A+4*HP),
                    ('f',COL_F),('g',COL_F+HP),('h',COL_F+2*HP),('i',COL_F+3*HP),('j',COL_F+4*HP)]:
        cx = bbx+base+HP//2
        txt(cx,bby+ROW_TOP-10,cn,sz=8,fill="#666",anchor="middle",bold=True)
        txt(cx,bby+ROW_TOP+NR*HP+14,cn,sz=8,fill="#666",anchor="middle",bold=True)

    # Rail polarity labels
    for side,xb in [('L',bbx+ML),('R',bbx+POS_R)]:
        txt(xb+HP//2,        bby+ROW_TOP-10, "+", sz=9,fill="#CC0000",bold=True)
        txt(xb+HP+HP//2,     bby+ROW_TOP-10 if side=='R' else bby+ROW_TOP-10, 
            "–", sz=9,fill="#0044CC",bold=True) if side=='L' else None
    # right rail labels  (POS=+, NEG=-)
    txt(bbx+POS_R+HP//2, bby+ROW_TOP-10, "+", sz=9,fill="#CC0000",bold=True)
    txt(bbx+NEG_R+HP//2, bby+ROW_TOP-10, "–", sz=9,fill="#0044CC",bold=True)
    txt(bbx+POS_L+HP//2, bby+ROW_TOP-10, "+", sz=9,fill="#CC0000",bold=True)
    txt(bbx+NEG_L+HP//2, bby+ROW_TOP-10, "–", sz=9,fill="#0044CC",bold=True)

    # Holes
    for row in range(1,NR+1):
        ry = row_y(bby, row)
        # row number
        txt(bbx+7, ry+4, str(row), sz=6, fill="#999", anchor="middle")
        # Rails
        for xoff in [NEG_L,POS_L,POS_R,NEG_R]:
            circ(bbx+xoff+HP//2, ry, 3.5, C["hole"], C["hole_s"], 0.5)
        # Component holes
        for base in [COL_A,COL_A+HP,COL_A+2*HP,COL_A+3*HP,COL_A+4*HP,
                     COL_F,COL_F+HP,COL_F+2*HP,COL_F+3*HP,COL_F+4*HP]:
            circ(bbx+base+HP//2, ry, 3.5, C["hole"], C["hole_s"], 0.5)

    # Player label above
    rect(bbx+BB_W//2-80, bby-28, 160, 22, C["hdr"], rx=5)
    txt(bbx+BB_W//2, bby-12, player_label, sz=12, fill="#FFFFFF", bold=True)

def mark_hole(bbx, bby, col, row, color, r=5):
    """Highlight a used hole"""
    circ(col_x(bbx,col), row_y(bby,row), r, color, C["white"], 1)

def mark_rail(bbx, bby, side, pol, row, color, r=5):
    circ(rail_x(bbx,side,pol), row_y(bby,row), r, color, C["white"], 1)

def wire(pts, color, sw=2.5):
    poly(pts, color, sw)

# ── Draw both bare breadboards ─────────────────────────────────────────────────
draw_breadboard(BB1_X, BB_Y, "PLAYER 1")
draw_breadboard(BB2_X, BB_Y, "PLAYER 2")

# ── ESP32-S3 CAM chip overlay ──────────────────────────────────────────────────
# The Freenove ESP32-S3 CAM spans rows 1-16 across the breadboard center gap
# Left pins (col e), Right pins (col f): rows 1-16
ESP_ROWS = 16

def draw_esp32(bbx, bby):
    # chip body
    cx1 = col_x(bbx,'e') - 2
    cx2 = col_x(bbx,'f') + 2
    ey1 = row_y(bby,1) - HP//2
    ey2 = row_y(bby,ESP_ROWS) + HP//2
    cw = cx2-cx1
    ch = ey2-ey1
    rect(cx1,ey1,cw,ch,C["esp_pcb"],"#0D47A1",1.5,rx=3)
    txt((cx1+cx2)//2,ey1+14,"ESP32-S3",sz=9,fill="#90CAF9",bold=True)
    txt((cx1+cx2)//2,ey1+25,"CAM",sz=8,fill="#BBDEFB",bold=True)
    # Camera module indicator (small rectangle inside)
    cm_w,cm_h = cw-10, 18
    rect(cx1+5,ey1+ch//2-cm_h//2,cm_w,cm_h,"#0D47A1","#42A5F5",1,rx=2)
    txt((cx1+cx2)//2,ey1+ch//2+5,"📷 OV2640",sz=7,fill="#90CAF9")
    # USB indicator at top
    rect(cx1+cw//2-8,ey1-8,16,8,"#37474F","#78909C",1,rx=1)
    txt((cx1+cx2)//2,ey1-1,"USB",sz=5,fill="#B0BEC5",anchor="middle")

    # Pin labels — LEFT side (col e = right contact of left half)
    # Freenove ESP32-S3 CAM left-side pinout (top to bottom):
    left_pins = [
        ("GND",   C["w_gnd"]),
        ("3.3V",  C["w_3v3"]),
        ("IO0",   "#555"),
        ("IO1",   "#555"),
        ("IO2",   "#555"),
        ("IO3",   "#555"),
        ("IO4",   "#555"),
        ("IO5",   "#555"),
        ("IO6",   "#555"),
        ("IO7",   "#555"),
        ("IO8",   "#555"),
        ("IO9",   "#555"),
        ("IO10",  "#555"),
        ("IO11",  "#555"),
        ("IO12",  "#555"),
        ("IO13",  "#555"),
    ]
    # Right side pinout:
    right_pins = [
        ("5V",    "#BB6600"),
        ("GND",   C["w_gnd"]),
        ("IO14",  "#555"),
        ("IO15",  "#555"),
        ("IO16",  "#555"),
        ("IO17",  "#555"),
        ("IO18",  "#555"),
        ("IO38",  "#555"),
        ("IO39",  "#555"),
        ("IO40",  C["w_bclk"]),   # BCLK
        ("IO41",  C["w_ws"]),     # WS
        ("IO42",  C["w_dout"]),   # DOUT
        ("IO43",  "#555"),
        ("IO44",  "#555"),
        ("IO45",  "#555"),
        ("IO46",  "#555"),
    ]

    for i,(name,col) in enumerate(left_pins[:ESP_ROWS]):
        ry = row_y(bby, i+1)
        px = cx1 - 2
        txt(px-2, ry+3, name, sz=6.5, fill=col, anchor="end")
        # pin dot on chip edge
        circ(cx1, ry, 2.5, col, "none")

    for i,(name,col) in enumerate(right_pins[:ESP_ROWS]):
        ry = row_y(bby, i+1)
        px = cx2 + 2
        txt(px+2, ry+3, name, sz=6.5, fill=col, anchor="start")
        circ(cx2, ry, 2.5, col, "none")

# ── PCM5102A DAC module overlay ────────────────────────────────────────────────
# DAC placed at rows 20-26, columns c through h (spans center gap)
DAC_ROW_START = 20
DAC_ROW_END   = 26

def draw_dac(bbx, bby):
    dx1 = col_x(bbx,'c') - HP//2
    dx2 = col_x(bbx,'h') + HP//2
    dy1 = row_y(bby,DAC_ROW_START) - HP//2
    dy2 = row_y(bby,DAC_ROW_END) + HP//2
    dw = dx2-dx1
    dh = dy2-dy1
    rect(dx1,dy1,dw,dh,C["dac_pcb"],"#2E7D32",1.5,rx=3)
    txt((dx1+dx2)//2,dy1+13,"PCM5102A",sz=9,fill="#A5D6A7",bold=True)
    txt((dx1+dx2)//2,dy1+24,"I²S DAC",sz=7,fill="#C8E6C9")
    # 3.5mm jack indicator
    rect(dx1+dw-20,dy1+dh//2-10,18,20,"#1B5E20","#81C784",1,rx=2)
    txt(dx1+dw-11,dy1+dh//2+4,"🎧",sz=8)

    # DAC top-row pin labels (left to right at row DAC_ROW_START)
    # Standard PCM5102A breakout: SCK BCK DIN LCK GND VCC
    # We'll place them at cols c,d,e,f,g,h
    dac_pins = [
        ("c", "SCK",  C["w_sck"]),
        ("d", "BCK",  C["w_bclk"]),
        ("e", "DIN",  C["w_dout"]),
        ("f", "LCK",  C["w_ws"]),
        ("g", "GND",  C["w_gnd"]),
        ("h", "VCC",  C["w_3v3"]),
    ]
    for col,name,col_c in dac_pins:
        px = col_x(bbx,col)
        py = dy1
        txt(px, py-4, name, sz=6.5, fill=col_c, anchor="middle", bold=True)
        circ(px, py, 2.5, col_c, "none")

# ── Wire routing helper ────────────────────────────────────────────────────────
def draw_wiring(bbx, bby):
    """Draw all the wires for one player setup"""

    # 1) 3.3V: left rail + → ESP row 2 (3.3V pin) col e
    r3v3_x = rail_x(bbx,'L','+')
    # Connect rows 1-NR of left + rail together (red line along rail)
    ln(r3v3_x, row_y(bby,1), r3v3_x, row_y(bby,NR), C["w_3v3"], 2)

    # ESP 3.3V pin (row 2, left side = col e) to left + rail
    mark_hole(bbx,bby,'e',2,C["w_3v3"])
    mark_rail(bbx,bby,'L','+',2,C["w_3v3"])
    wire([(col_x(bbx,'e'), row_y(bby,2)), (r3v3_x, row_y(bby,2))], C["w_3v3"])

    # ESP GND (row 1, col e) to left – rail
    gnd_l_x = rail_x(bbx,'L','-')
    ln(gnd_l_x, row_y(bby,1), gnd_l_x, row_y(bby,NR), C["w_gnd"], 2)
    mark_hole(bbx,bby,'e',1,C["w_gnd"])
    mark_rail(bbx,bby,'L','-',1,C["w_gnd"])
    wire([(col_x(bbx,'e'),row_y(bby,1)),(gnd_l_x,row_y(bby,1))], C["w_gnd"])

    # Right side: 5V at row 1 col f (not connected to breadboard rails in this build)
    # GND at row 2 col f → right – rail
    gnd_r_x = rail_x(bbx,'R','-')
    mark_hole(bbx,bby,'f',2,C["w_gnd"])
    mark_rail(bbx,bby,'R','-',2,C["w_gnd"])
    wire([(col_x(bbx,'f'),row_y(bby,2)),(gnd_r_x,row_y(bby,2))], C["w_gnd"])
    ln(gnd_r_x, row_y(bby,1), gnd_r_x, row_y(bby,NR), C["w_gnd"], 2)

    # Cross-connect GND rails (bottom)
    wire([(gnd_l_x,row_y(bby,NR)),(gnd_r_x,row_y(bby,NR))], C["w_gnd"])
    # Cross-connect + rails for DAC VCC (row DAC_ROW_START)
    r3v3_r_x = rail_x(bbx,'R','+')
    ln(r3v3_r_x, row_y(bby,1), r3v3_r_x, row_y(bby,NR), C["w_3v3"], 2)
    wire([(r3v3_x,row_y(bby,NR-2)),(r3v3_r_x,row_y(bby,NR-2))], C["w_3v3"])

    # I2S wires from ESP32 right-side pins to DAC
    # IO40 = row 10, col f side → BCLK (BCK on DAC col d)
    io40_row = 10
    io41_row = 11
    io42_row = 12

    # BCLK: ESP IO40 (f, row 10) → DAC BCK (col d, row DAC_ROW_START)
    mark_hole(bbx,bby,'f',io40_row,C["w_bclk"])
    mark_hole(bbx,bby,'d',DAC_ROW_START,C["w_bclk"])
    bclk_pts = [
        (col_x(bbx,'f'),       row_y(bby,io40_row)),
        (col_x(bbx,'f')+30,    row_y(bby,io40_row)),
        (col_x(bbx,'f')+30,    row_y(bby,DAC_ROW_START)-20),
        (col_x(bbx,'d'),       row_y(bby,DAC_ROW_START)-20),
        (col_x(bbx,'d'),       row_y(bby,DAC_ROW_START)),
    ]
    wire(bclk_pts, C["w_bclk"])

    # WS: ESP IO41 (f, row 11) → DAC LCK (col f, row DAC_ROW_START)
    mark_hole(bbx,bby,'f',io41_row,C["w_ws"])
    mark_hole(bbx,bby,'f',DAC_ROW_START,C["w_ws"])
    ws_pts = [
        (col_x(bbx,'f'),   row_y(bby,io41_row)),
        (col_x(bbx,'f'),   row_y(bby,DAC_ROW_START)),
    ]
    wire(ws_pts, C["w_ws"])

    # DOUT: ESP IO42 (f, row 12) → DAC DIN (col e, row DAC_ROW_START)
    mark_hole(bbx,bby,'f',io42_row,C["w_dout"])
    mark_hole(bbx,bby,'e',DAC_ROW_START,C["w_dout"])
    dout_pts = [
        (col_x(bbx,'f'),       row_y(bby,io42_row)),
        (col_x(bbx,'f')-25,    row_y(bby,io42_row)),
        (col_x(bbx,'f')-25,    row_y(bby,DAC_ROW_START)-12),
        (col_x(bbx,'e'),       row_y(bby,DAC_ROW_START)-12),
        (col_x(bbx,'e'),       row_y(bby,DAC_ROW_START)),
    ]
    wire(dout_pts, C["w_dout"])

    # SCK: DAC col c → GND (col c, row 28) → GND rail
    mark_hole(bbx,bby,'c',DAC_ROW_START,C["w_sck"])
    mark_hole(bbx,bby,'c',28,C["w_gnd"])
    wire([(col_x(bbx,'c'),row_y(bby,DAC_ROW_START)),(col_x(bbx,'c'),row_y(bby,28))],C["w_sck"])
    wire([(col_x(bbx,'c'),row_y(bby,28)),(gnd_l_x,row_y(bby,28))],C["w_gnd"],sw=1.5)
    mark_rail(bbx,bby,'L','-',28,C["w_gnd"])

    # DAC VCC (col h row 20) → right + rail
    mark_hole(bbx,bby,'h',DAC_ROW_START,C["w_3v3"])
    mark_rail(bbx,bby,'R','+',DAC_ROW_START,C["w_3v3"])
    wire([(col_x(bbx,'h'),row_y(bby,DAC_ROW_START)),(r3v3_r_x,row_y(bby,DAC_ROW_START))],C["w_3v3"])

    # DAC GND (col g row 20) → right – rail
    mark_hole(bbx,bby,'g',DAC_ROW_START,C["w_gnd"])
    mark_rail(bbx,bby,'R','-',DAC_ROW_START,C["w_gnd"])
    wire([(col_x(bbx,'g'),row_y(bby,DAC_ROW_START)),(gnd_r_x,row_y(bby,DAC_ROW_START))],C["w_gnd"])

    # Signal labels at wire midpoints
    label_pill(bclk_pts[2][0],bclk_pts[2][1],"BCLK",C["w_bclk"],"#FFF",w=40)
    label_pill(col_x(bbx,'f')-40,(row_y(bby,io41_row)+row_y(bby,DAC_ROW_START))//2,"WS",C["w_ws"],"#FFF",w=30)
    label_pill(col_x(bbx,'f')-40,(row_y(bby,io42_row)+row_y(bby,DAC_ROW_START))//2,"DOUT",C["w_dout"],"#FFF",w=38)

draw_esp32(BB1_X, BB_Y)
draw_dac(BB1_X, BB_Y)
draw_wiring(BB1_X, BB_Y)

draw_esp32(BB2_X, BB_Y)
draw_dac(BB2_X, BB_Y)
draw_wiring(BB2_X, BB_Y)

# Legend for breadboard section
LEG_X = BB2_X + BB_W + 30
LEG_Y = BB_Y + 20
rect(LEG_X, LEG_Y, 150, 220, "#ECEFF1", "#B0BEC5", 1, rx=6)
txt(LEG_X+75, LEG_Y+16, "WIRE LEGEND", sz=10, fill="#37474F", bold=True)
legend_items = [
    (C["w_3v3"],  "3.3 V power"),
    (C["w_gnd"],  "GND"),
    (C["w_bclk"], "BCLK (I²S)"),
    (C["w_ws"],   "WS/LRCLK"),
    (C["w_dout"], "DOUT→DIN"),
    (C["w_sck"],  "SCK→GND"),
]
for i,(col,name) in enumerate(legend_items):
    lx = LEG_X+14
    ly = LEG_Y+34+i*28
    rect(lx,ly-6,24,12,col,rx=3)
    txt(lx+30,ly+4,name,sz=9,fill="#333",anchor="start")

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMATIC DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════
SCH_Y0 = BB_Y + BB_H + 60
section_header(SCH_Y0 - 34, "SCHEMATIC DIAGRAM  (one player shown — both identical)")

# Draw a clean schematic for one player, centered
SCH_CX = W//2
SCH_Y = SCH_Y0 + 20

# ESP32 box
ESP_W, ESP_H = 200, 280
ESP_X = SCH_CX - 260
ESP_Y = SCH_Y + 60

rect(ESP_X,ESP_Y,ESP_W,ESP_H,"#E3F2FD","#1A237E",2,rx=6)
txt(ESP_X+ESP_W//2,ESP_Y+18,"Freenove",sz=10,fill="#1A237E",bold=True)
txt(ESP_X+ESP_W//2,ESP_Y+32,"ESP32-S3 CAM",sz=11,fill="#1A237E",bold=True)

# ESP32 pins on right side (output side)
sch_pins_esp = [
    (0.15, "3.3V",   C["w_3v3"],  "pwr"),
    (0.28, "GND",    C["w_gnd"],  "pwr"),
    (0.45, "IO40",   C["w_bclk"], "BCLK"),
    (0.58, "IO41",   C["w_ws"],   "WS"),
    (0.71, "IO42",   C["w_dout"], "DOUT"),
    (0.85, "USB-C",  "#607D8B",   "power\nin"),
]

ESP_RIGHT_X = ESP_X + ESP_W
for frac, name, col, sig in sch_pins_esp:
    py = int(ESP_Y + frac*ESP_H)
    circ(ESP_RIGHT_X, py, 4, col, "#FFF", 1)
    txt(ESP_RIGHT_X-8, py+4, name, sz=8, fill=col, anchor="end", bold=True)
    txt(ESP_RIGHT_X+8, py+4, sig, sz=8, fill=col, anchor="start", italic=True)

# DAC box
DAC_W, DAC_H = 180, 240
DAC_X = SCH_CX + 80
DAC_Y = ESP_Y + 20

rect(DAC_X,DAC_Y,DAC_W,DAC_H,"#E8F5E9","#1B5E20",2,rx=6)
txt(DAC_X+DAC_W//2,DAC_Y+18,"PCM5102A",sz=11,fill="#1B5E20",bold=True)
txt(DAC_X+DAC_W//2,DAC_Y+32,"I²S DAC",sz=10,fill="#2E7D32")
txt(DAC_X+DAC_W//2,DAC_Y+DAC_H-20,"🎵 3.5mm OUT",sz=9,fill="#388E3C")

sch_pins_dac = [
    (0.15, "VCC",  C["w_3v3"],  "3.3V"),
    (0.28, "GND",  C["w_gnd"],  "0V"),
    (0.45, "BCK",  C["w_bclk"], "BCLK"),
    (0.58, "LCK",  C["w_ws"],   "LRCLK"),
    (0.71, "DIN",  C["w_dout"], "Data"),
    (0.84, "SCK",  C["w_sck"],  "→GND"),
]

DAC_LEFT_X = DAC_X
for frac, name, col, sig in sch_pins_dac:
    py = int(DAC_Y + frac*DAC_H)
    circ(DAC_LEFT_X, py, 4, col, "#FFF", 1)
    txt(DAC_LEFT_X+8, py+4, name, sz=8, fill=col, anchor="start", bold=True)
    txt(DAC_LEFT_X-8, py+4, sig, sz=8, fill=col, anchor="end", italic=True)

# Connecting wires
connections = [
    (0.15, "#E8F5E9", 0.15, C["w_3v3"]),   # 3.3V
    (0.28, "#E8F5E9", 0.28, C["w_gnd"]),    # GND
    (0.45, "#E8F5E9", 0.45, C["w_bclk"]),   # BCLK
    (0.58, "#E8F5E9", 0.58, C["w_ws"]),     # WS
    (0.71, "#E8F5E9", 0.71, C["w_dout"]),   # DOUT
]

esp_fracs = [0.15,0.28,0.45,0.58,0.71]
dac_fracs = [0.15,0.28,0.45,0.58,0.71]
wire_colors= [C["w_3v3"],C["w_gnd"],C["w_bclk"],C["w_ws"],C["w_dout"]]
wire_labels= ["3.3V","GND","BCLK","WS/LRCLK","DOUT→DIN"]

for ef,df,wc,wl in zip(esp_fracs,dac_fracs,wire_colors,wire_labels):
    ey = int(ESP_Y + ef*ESP_H)
    dy = int(DAC_Y + df*DAC_H)
    mx = (ESP_RIGHT_X + DAC_LEFT_X)//2
    pts = [(ESP_RIGHT_X,ey),(mx,ey),(mx,dy),(DAC_LEFT_X,dy)]
    wire(pts, wc, sw=2.5)
    txt(mx, (ey+dy)//2+4, wl, sz=8, fill=wc, bold=True)

# Power supply annotation
PWR_X = ESP_X - 100
txt(PWR_X+35, ESP_Y+0.15*ESP_H+4, "3.3V", sz=9, fill=C["w_3v3"], bold=True, anchor="middle")
txt(PWR_X+35, ESP_Y+0.28*ESP_H+4, "GND",  sz=9, fill=C["w_gnd"], bold=True, anchor="middle")
ln(PWR_X+70,int(ESP_Y+0.15*ESP_H),ESP_X,int(ESP_Y+0.15*ESP_H), C["w_3v3"],2)
ln(PWR_X+70,int(ESP_Y+0.28*ESP_H),ESP_X,int(ESP_Y+0.28*ESP_H), C["w_gnd"],2)
rect(PWR_X,ESP_Y+0.1*ESP_H-6,70,40,"#FFF9C4","#F9A825",1.5,rx=4)
txt(PWR_X+35,ESP_Y+0.1*ESP_H+4,"USB-C →",sz=8,fill="#E65100",bold=True)
txt(PWR_X+35,ESP_Y+0.1*ESP_H+16,"on-board",sz=7,fill="#795548")
txt(PWR_X+35,ESP_Y+0.1*ESP_H+26,"3.3V LDO",sz=7,fill="#795548")

# SCK→GND note
sck_y = int(DAC_Y + 0.84*DAC_H)
gnd_sym_x = DAC_X + DAC_W + 40
ln(DAC_X+DAC_W,sck_y,gnd_sym_x,sck_y,C["w_sck"],2)
ln(gnd_sym_x,sck_y,gnd_sym_x,sck_y+16,C["w_sck"],2)
ln(gnd_sym_x-10,sck_y+16,gnd_sym_x+10,sck_y+16,C["w_sck"],2)
ln(gnd_sym_x-6,sck_y+20,gnd_sym_x+6,sck_y+20,C["w_sck"],1.5)
ln(gnd_sym_x-2,sck_y+24,gnd_sym_x+2,sck_y+24,C["w_sck"],1)
txt(gnd_sym_x,sck_y-6,"SCK→GND",sz=7,fill=C["w_sck"],italic=True)

# FMT/XMT solder bridge note
rect(DAC_X+DAC_W+20,DAC_Y+10,120,50,"#FFF3E0","#FF6F00",1,rx=4)
txt(DAC_X+DAC_W+80,DAC_Y+22,"Solder pads",sz=8,fill="#E65100",bold=True)
txt(DAC_X+DAC_W+80,DAC_Y+35,"FMT→GND (I²S)",sz=7,fill="#5D4037")
txt(DAC_X+DAC_W+80,DAC_Y+47,"XMT→3.3V (unmute)",sz=7,fill="#5D4050")

SCH_BOTTOM = DAC_Y + DAC_H + 30

# ═══════════════════════════════════════════════════════════════════════════════
# CONNECTION TABLE
# ═══════════════════════════════════════════════════════════════════════════════
TBL_Y = SCH_BOTTOM + 50
section_header(TBL_Y - 34, "CONNECTION TABLE  (per player — repeat identically for Player 2)")

TBL_X = 80
TBL_W = W - 160
COL_WIDTHS = [160,160,140,140,200,240]  # signal,esp_gpio,esp_pin,dac_pin,dac_conn,notes
COL_LABELS  = ["Signal","ESP32-S3 GPIO","ESP Breadboard","DAC Pin","DAC Breadboard","Notes"]

# Table header
rx = TBL_X
for i,(cw,cl) in enumerate(zip(COL_WIDTHS,COL_LABELS)):
    rect(rx,TBL_Y,cw,28,C["table_h"])
    txt(rx+cw//2,TBL_Y+18,cl,sz=10,fill="#FFF",bold=True)
    rx+=cw

rows_data = [
    (C["w_3v3"],  ["3.3V Power","3.3V pin","Left col e, row 2","VCC (pin 6)","Col h, row 20","Breadboard left + rail → DAC right + rail"]),
    (C["w_gnd"],  ["GND","GND pin","Left col e, row 1","GND (pin 5)","Col g, row 20","Both GND rails bridged at bottom"]),
    (C["w_bclk"], ["BCLK (Bit Clk)","GPIO 40","Right col f, row 10","BCK (pin 2)","Col d, row 20","Orange wire — I²S bit clock"]),
    (C["w_ws"],   ["WS / LRCLK","GPIO 41","Right col f, row 11","LCK (pin 4)","Col f, row 20","Purple wire — left/right select"]),
    (C["w_dout"], ["DOUT (Data Out)","GPIO 42","Right col f, row 12","DIN (pin 3)","Col e, row 20","Green wire — serial audio data"]),
    (C["w_sck"],  ["SCK (sys clk)","— (not used)","—","SCK (pin 1)","Col c, row 20","Tie to GND → enables internal PLL"]),
    ("#607D8B",   ["FMT (format)","— (solder pad)","—","FMT pad","DAC bottom pad","Solder pad: bridge to GND for I²S"]),
    ("#880E4F",   ["XMT (mute)","— (solder pad)","—","XMT pad","DAC bottom pad","Solder pad: bridge to 3.3V to unmute"]),
]

for ri,(rc,rd) in enumerate(rows_data):
    ry2 = TBL_Y + 28 + ri*26
    bg = C["table_r1"] if ri%2==0 else C["table_r2"]
    rect(TBL_X,ry2,TBL_W,26,bg)
    # colour swatch in first col
    rect(TBL_X+4,ry2+6,18,14,rc,rx=2)
    rxc = TBL_X+COL_WIDTHS[0]
    for ci,cv in enumerate(rd):
        cxc = TBL_X + sum(COL_WIDTHS[:ci])
        anchor = "start" if ci>=2 else "middle"
        xoff = 4 if anchor=="start" else COL_WIDTHS[ci]//2
        if ci==0:
            txt(cxc+26, ry2+17, cv, sz=9, fill=rc, anchor="start", bold=True)
        else:
            txt(cxc+xoff, ry2+17, cv, sz=9, fill="#263238", anchor=anchor)
    ln(TBL_X,ry2+26,TBL_X+TBL_W,ry2+26,"#B0BEC5",0.5)

TBL_BOTTOM = TBL_Y + 28 + len(rows_data)*26
rect(TBL_X,TBL_Y,TBL_W,28+len(rows_data)*26,"none","#90A4AE",1,rx=2)

# ═══════════════════════════════════════════════════════════════════════════════
# SQUEEZELITE-ESP32 CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
CFG_Y = TBL_BOTTOM + 55
section_header(CFG_Y - 34, "RECOMMENDED SQUEEZELITE-ESP32 CONFIGURATION")

# Two-column config layout
CFG_LEFT  = 60
CFG_RIGHT = W//2 + 20
CFG_COL_W = W//2 - 80

# Left column: NVS/settings
rect(CFG_LEFT,CFG_Y,CFG_COL_W,340,"#E8EAF6","#3949AB",1.5,rx=8)
txt(CFG_LEFT+CFG_COL_W//2,CFG_Y+20,"NVS / Web-UI Settings (squeezelite-esp32)",sz=12,fill="#1A237E",bold=True)

cfg_settings = [
    ("i2s_config",  '{"bck_io_num":40,"ws_io_num":41,"data_out_io_num":42}'),
    ("dac_config",  '"model":"I2S","port":"0","i2c_addr":""'),
    ("",            "  (no I²C needed — PCM5102A is I²S only)"),
    ("output_type", '"I2S"'),
    ("",            ""),
    ("PSRAM note",  "ESP32-S3 CAM uses PSRAM on GPIO 26-32"),
    ("",            "→ these GPIOs must NOT be used for I²S"),
    ("",            "→ GPIO 40/41/42 are safe ✓"),
    ("Camera note", "OV2640 uses GPIO 1-18, XCLK, I²C"),
    ("",            "→ I²S on 40/41/42 has zero conflict ✓"),
    ("Boot pins",   "Avoid GPIO 0 (boot), 45, 46 (strapping)"),
    ("USB pins",    "Avoid GPIO 19, 20 (USB D+/D-)"),
]

for i,(k,v) in enumerate(cfg_settings):
    ly = CFG_Y+40+i*22
    if k:
        rect(CFG_LEFT+10,ly-12,100,16,"#3949AB",rx=2)
        txt(CFG_LEFT+14,ly,k,sz=8,fill="#FFF",anchor="start",bold=True)
        txt(CFG_LEFT+118,ly,v,sz=8,fill="#283593",anchor="start",ff="Courier New,monospace")
    else:
        txt(CFG_LEFT+118,ly,v,sz=8,fill="#455A64",anchor="start",italic=True)

# Right column: caveats and tips
rect(CFG_RIGHT,CFG_Y,CFG_COL_W,340,"#FFF8E1","#F57F17",1.5,rx=8)
txt(CFG_RIGHT+CFG_COL_W//2,CFG_Y+20,"Caveats & Assembly Tips",sz=12,fill="#E65100",bold=True)

tips = [
    ("⚡","Power","Feed USB-C into ESP32; 3.3V from on-board LDO → DAC"),
    ("🔇","Noise","Add 100nF cap across DAC VCC/GND near the module"),
    ("🌡️","Current","PCM5102A draws ~15mA; ESP LDO handles it fine"),
    ("📷","Camera vs Audio","Camera and audio can run simultaneously; separate tasks"),
    ("🔁","PSRAM","CAM board has PSRAM; Squeezelite uses it for audio buffer"),
    ("🔊","Volume","Set XMT pad HIGH (3.3V) — factory default is muted!"),
    ("🎛️","Filter","FMT=GND selects I²S format; FLT=GND = normal roll-off"),
    ("🔌","Audio out","3.5mm jack on DAC is line-level; add amp for speakers"),
    ("🐛","Debug","Serial monitor at 115200 on GPIO 43(TX)/44(RX)"),
    ("💡","Flash","Hold BOOT (GPIO0) + press RESET to enter flash mode"),
    ("🔄","Players","Both players are wired identically; flash each separately"),
]

for i,(icon,title,desc) in enumerate(tips):
    ty = CFG_Y+42+i*27
    txt(CFG_RIGHT+16,ty,icon,sz=11,anchor="start")
    txt(CFG_RIGHT+32,ty,title+":",sz=9,fill="#BF360C",anchor="start",bold=True)
    txt(CFG_RIGHT+95,ty,desc,sz=8.5,fill="#4E342E",anchor="start")

# ═══════════════════════════════════════════════════════════════════════════════
# GPIO PINOUT REFERENCE TABLE
# ═══════════════════════════════════════════════════════════════════════════════
GPIO_Y = CFG_Y + 360
section_header(GPIO_Y - 34, "FREENOVE ESP32-S3 CAM — GPIO USAGE MAP  (inferred from board documentation)")

# Two mini tables: left=used by camera, right=used by I2S
MT_X = 100
MT_Y = GPIO_Y + 10
MT_W = 360
MT_H = 200

# Camera GPIOs table
rect(MT_X,MT_Y,MT_W,MT_H,"#FCE4EC","#C62828",1.5,rx=6)
txt(MT_X+MT_W//2,MT_Y+18,"⛔ Camera GPIOs — DO NOT USE for I²S",sz=10,fill="#B71C1C",bold=True)
cam_gpios = [
    ("XCLK","GPIO 15"),("PCLK","GPIO 13"),("VSYNC","GPIO 6"),("HREF","GPIO 7"),
    ("D0","GPIO 11"),("D1","GPIO 9"),("D2","GPIO 8"),("D3","GPIO 10"),
    ("D4","GPIO 12"),("D5","GPIO 18"),("D6","GPIO 17"),("D7","GPIO 16"),
    ("SDA","GPIO 4"),("SCL","GPIO 5"),
]
for i,(sig,gpio) in enumerate(cam_gpios):
    col = i//7
    row = i%7
    gx = MT_X+10+col*170
    gy = MT_Y+32+row*24
    rect(gx,gy-12,155,20,"#FFCDD2",rx=3)
    txt(gx+8,gy,"⚠ "+sig,sz=8,fill="#C62828",anchor="start",bold=True)
    txt(gx+155-8,gy,gpio,sz=8,fill="#37474F",anchor="end")

# Safe I2S GPIOs table
rect(MT_X+MT_W+40,MT_Y,MT_W,MT_H,"#E8F5E9","#1B5E20",1.5,rx=6)
txt(MT_X+MT_W+40+MT_W//2,MT_Y+18,"✅ Safe GPIOs for I²S + Other Uses",sz=10,fill="#1B5E20",bold=True)
safe_gpios = [
    ("BCLK ← USE","GPIO 40","orange"),
    ("WS   ← USE","GPIO 41","purple"),
    ("DOUT ← USE","GPIO 42","green"),
    ("TX (debug)","GPIO 43","gray"),
    ("RX (debug)","GPIO 44","gray"),
    ("Available","GPIO 38","gray"),
    ("Available","GPIO 39","gray"),
    ("BOOT button","GPIO 0","red"),
    ("Strapping","GPIO 45,46","red"),
    ("USB D-/D+","GPIO 19,20","red"),
    ("PSRAM bus","GPIO 26-32","red"),
]
sx2 = MT_X+MT_W+40
for i,(sig,gpio,col) in enumerate(safe_gpios):
    c2 = i//6
    r2 = i%6
    gx = sx2+10+c2*180
    gy = MT_Y+32+r2*27
    bg = {"orange":"#FFF3E0","purple":"#EDE7F6","green":"#E8F5E9","gray":"#ECEFF1","red":"#FFEBEE"}[col]
    fc = {"orange":C["w_bclk"],"purple":C["w_ws"],"green":C["w_dout"],"gray":"#455A64","red":"#C62828"}[col]
    prefix = "✅ " if col in ("orange","purple","green") else "— "
    rect(gx,gy-14,165,22,bg,rx=3)
    txt(gx+6,gy,prefix+sig,sz=8,fill=fc,anchor="start",bold=(col!="gray"))
    txt(gx+165-4,gy,gpio,sz=8,fill="#37474F",anchor="end")

# ── Footer ─────────────────────────────────────────────────────────────────────
FOOTER_Y = GPIO_Y + MT_H + 50
rect(0,FOOTER_Y,W,60,"#263238")
txt(W//2,FOOTER_Y+22,"Generated for: Freenove ESP32-S3 CAM + Teyleten PCM5102A  |  Squeezelite-ESP32 Dual Player",
    sz=12,fill="#90A4AE")
txt(W//2,FOOTER_Y+40,
    "Pinout inferred from Freenove FNK0093 documentation. Verify SCK/FMT/XMT solder bridges on your specific PCM5102A module revision.",
    sz=10,fill="#546E7A",italic=True)

o('</svg>')

svg_text = "\n".join(lines)
with open("/home/user/squeeze-esp32-builds-/wiring_diagram.svg","w") as f:
    f.write(svg_text)

print(f"SVG written: {len(svg_text)} bytes, {len(lines)} elements")
print("Output: /home/user/squeeze-esp32-builds-/wiring_diagram.svg")
