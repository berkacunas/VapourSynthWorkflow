

class EncoderSettings:
    
    def __init__(self, encoder: str = "libx265", crf: int = 18, preset: str = "fast") -> None:
        
        self.encoder = encoder
        self.crf = crf
        self.preset = preset