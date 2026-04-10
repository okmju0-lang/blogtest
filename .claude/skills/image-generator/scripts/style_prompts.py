"""
이미지 생성 스타일 프롬프트 정의

Nano Banana 2 (gemini-3.1-flash-image-preview) 이미지 생성 시
스타일별 프롬프트 프리픽스를 제공한다.
"""

STYLE_PROMPTS = {
    "graphic-recording": (
        "Create an educational infographic in a warm, hand-drawn graphic recording style. "
        "Use warm colors (wine #593C47, gold #F2C53D, orange #F25C05, yellow #F2E63D) on cream background. "
        "Include hand-drawn boxes, arrows, banners, speech bubbles. "
        "Use simple icons and emojis. "
        "Include clear Korean labels and short text annotations on each element. "
        "Clean, readable, educational infographic with text."
    ),
    "modern": (
        "Create a clean, modern educational diagram. "
        "Use indigo (#4361EE) and cyan (#4CC9F0) color scheme on white background. "
        "Minimalist design with geometric shapes, clean lines, subtle gradients. "
        "Include clear Korean labels and short text annotations on each element. "
        "Professional tech/startup infographic with labeled diagrams."
    ),
    "ax-vivid": (
        "Create a vibrant AI transformation themed educational infographic. "
        "Use deep blue (#1E3A8A) and purple (#7C3AED) as the dominant colors, with electric blue (#3B82F6) and violet (#8B5CF6) accents on a white background. "
        "Include bold colored geometric shapes, smooth gradient arrows, and glowing node-and-connection elements that evoke data flow and AI networks. "
        "Include clear Korean labels and short text annotations on each element. "
        "Modern, energetic, AI product design aesthetic. No black-and-white, full color infographic."
    ),
    "corporate": (
        "Create a professional corporate educational diagram. "
        "Navy (#1B2A4A) and gold (#C9A84C) color scheme. "
        "Formal, clean, structured layout with professional icons. "
        "Include clear Korean labels and short text annotations on each element. "
        "Suitable for executive presentation. Labeled infographic."
    ),

}
