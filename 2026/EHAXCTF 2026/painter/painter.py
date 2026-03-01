import sys

x, y = 0, 0
X, Y = [], []

try:
    with open("mouse_data.txt", "r") as f:
        for line in f:
            line = line.strip()
            if len(line) >= 14:
                btn = int(line[0:2], 16)
                dx_bytes = bytes.fromhex(line[4:8])
                dy_bytes = bytes.fromhex(line[8:12])
                
                dx = int.from_bytes(dx_bytes, byteorder='little', signed=True)
                dy = int.from_bytes(dy_bytes, byteorder='little', signed=True)
                
                x += dx
                y += dy 
                
                if btn == 1:
                    X.append(x)
                    Y.append(y)
except FileNotFoundError:
    sys.exit("Error: mouse_data.txt 파일을 찾을 수 없습니다.")

if not X:
    sys.exit("Error: 그리기 데이터를 찾을 수 없습니다.")

min_x, max_x = min(X), max(X)
min_y, max_y = min(Y), max(Y)
width = max_x - min_x + 50
height = max_y - min_y + 50

with open("flag_replay.html", "w") as f:
    f.write(f"""
    <html>
    <body style="background:#121212; color:#00ff00; font-family:monospace; text-align:center; padding: 20px;">
        <h2>CTF Flag Revealer (Deception Bypass)</h2>
        <p>슬라이더를 드래그하여 낙서가 시작되기 전의 진짜 플래그를 확인하세요.</p>
        <input type="range" id="slider" min="1" max="{len(X)}" value="{len(X)}" style="width:80%; cursor:pointer;" oninput="draw()">
        <br><br>
        <div style="overflow: auto; border: 2px solid #333; background: #000; display: inline-block;">
            <canvas id="canvas" width="{width}" height="{height}"></canvas>
        </div>
        <script>
            const X = {X};
            const Y = {Y};
            const minX = {min_x - 25};
            const minY = {min_y - 25};
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            function draw() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#00ff00";
                const limit = document.getElementById('slider').value;
                for(let i=0; i<limit; i++) {{
                    ctx.beginPath();
                    ctx.arc(X[i] - minX, Y[i] - minY, 2, 0, 2*Math.PI);
                    ctx.fill();
                }}
            }}
            draw();
        </script>
    </body>
    </html>
    """)

print("성공! 'flag_replay.html'이 생성되었습니다.")