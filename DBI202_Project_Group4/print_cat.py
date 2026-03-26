import base64

svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><circle cx="256" cy="256" r="240" fill="#3B82F6"/><ellipse cx="256" cy="300" rx="180" ry="140" fill="#FFFFFF"/><circle cx="210" cy="220" r="30" fill="black"/><circle cx="220" cy="210" r="10" fill="white"/><circle cx="302" cy="220" r="30" fill="black"/><circle cx="312" cy="210" r="10" fill="white"/><circle cx="256" cy="270" r="20" fill="#EF4444"/><path d="M256 290 v60" stroke="black" stroke-width="4"/><path d="M190 320 l-60 -10 M320 320 l60 -10 M190 340 l-50 10 M320 340 l50 10" stroke="black" stroke-width="4"/><polygon points="200,80 150,20 250,50" fill="#3B82F6"/><polygon points="312,80 362,20 262,50" fill="#3B82F6"/><rect x="200" y="440" width="112" height="20" fill="#FCD34D" rx="10"/></svg>"""

print(base64.b64encode(svg.encode('utf-8')).decode('utf-8'))
