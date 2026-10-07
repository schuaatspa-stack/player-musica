import pygame
import os
import yt_dlp
import customtkinter as ctk
from PIL import Image

class PlayerDeMusica:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.faixa_atual = None
        self.esta_tocando = False
        self.esta_pausado = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        self.duracao_total = 0
        self.posicao_inicial_segundos = 0

    def carregar_musica(self, caminho_da_musica):
        if os.path.exists(caminho_da_musica):
            self.faixa_atual = caminho_da_musica
            pygame.mixer.music.load(self.faixa_atual)
            try:
                audio = pygame.mixer.Sound(self.faixa_atual)
                self.duracao_total = audio.get_length()
            except:
                self.duracao_total = 0
            self.posicao_inicial_segundos = 0

    def carregar_do_youtube(self, busca):
        pasta_destino = "musica"
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
        self.parar()
        try:
            pygame.mixer.music.unload()
        except AttributeError:
            pass 
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'), 
            'writethumbnail': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{busca}", download=True)
                video_info = info['entries'][0]
                arquivo_bruto = ydl.prepare_filename(video_info)
                nome_base, _ = os.path.splitext(arquivo_bruto)
                caminho_final_mp3 = nome_base + ".mp3"
            
            if os.path.exists(caminho_final_mp3):
                self.carregar_musica(caminho_final_mp3)
                self.tocar()
        except Exception as e:
            print(f"Erro no YouTube: {e}")

    def tocar(self):
        if self.faixa_atual is None: return
        pygame.mixer.music.play(start=self.posicao_inicial_segundos)
        self.esta_tocando = True
        self.esta_pausado = False

    def pausar(self):
        if self.esta_tocando and not self.esta_pausado:
            pygame.mixer.music.pause()
            self.esta_pausado = True

    def retomar(self):
        if self.esta_pausado:
            pygame.mixer.music.unpause()
            self.esta_pausado = False

    def parar(self):
        pygame.mixer.music.stop()
        self.esta_tocando = False
        self.esta_pausado = False
        self.posicao_inicial_segundos = 0

    def buscar_posicao(self, segundos):
        if self.faixa_atual:
            self.posicao_inicial_segundos = segundos
            pygame.mixer.music.play(start=segundos)
            self.esta_tocando = True
            self.esta_pausado = False

    def avancar_musica(self, pasta="musica"):
        if not self.faixa_atual:
            if not os.path.exists(pasta): return
            arquivos = [f for f in os.listdir(pasta) if f.endswith(".mp3")]
            if arquivos:
                self.carregar_musica(os.path.join(pasta, arquivos[0]))
                self.tocar()
            return
            
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".mp3")]
        if not arquivos: return
            
        nome_atual = os.path.basename(self.faixa_atual)
        if nome_atual in arquivos:
            prox_indice = (arquivos.index(nome_atual) + 1) % len(arquivos)
            self.parar()
            self.carregar_musica(os.path.join(pasta, arquivos[prox_indice]))
            self.tocar()

    def voltar_musica(self, pasta="musica"):
        if not self.faixa_atual: return
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".mp3")]
        if not arquivos: return
            
        nome_atual = os.path.basename(self.faixa_atual)
        if nome_atual in arquivos:
            indice_atual = arquivos.index(nome_atual)
            prox_indice = indice_atual - 1 if indice_atual - 1 >= 0 else len(arquivos) - 1
            self.parar()
            self.carregar_musica(os.path.join(pasta, arquivos[prox_indice]))
            self.tocar()

class InterfacePlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.player = PlayerDeMusica()
        
        self.title("🎵 Player de Música")
        self.geometry("600x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # 1. BARRA DE PESQUISA YOUTUBE
        self.frame_yt = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_yt.pack(pady=15, fill="x", padx=20)
        
        self.entry_yt = ctk.CTkEntry(self.frame_yt, placeholder_text="Buscar música no YouTube...")
        self.entry_yt.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_yt.bind("<Return>", self.buscar_youtube)
        
        self.btn_yt = ctk.CTkButton(self.frame_yt, text="Reproduzir", width=80, command=self.buscar_youtube)
        self.btn_yt.pack(side="right")
        
        # 2. ESPAÇO PARA A CAPA DO ÁLBUM
        self.frame_capa = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_capa.pack(pady=10)
        
        self.lbl_capa = ctk.CTkLabel(self.frame_capa, text="🎵", font=("Arial", 80), width=180, height=180, fg_color="gray20", corner_radius=10)
        self.lbl_capa.pack()

        # 3. PLAYLIST
        self.playlist_frame = ctk.CTkScrollableFrame(self, height=120)
        self.playlist_frame.pack(pady=10, fill="both", expand=True, padx=20)
        self.atualizar_playlist()
        
        # 4. STATUS
        self.lbl_status = ctk.CTkLabel(self, text="Player Pronto", font=("Arial", 14, "bold"))
        self.lbl_status.pack(pady=(10, 0))

        # 5. BARRA DE PROGRESSO
        self.frame_tempo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tempo.pack(pady=5, fill="x", padx=40)
        
        self.lbl_tempo_atual = ctk.CTkLabel(self.frame_tempo, text="00:00", width=40)
        self.lbl_tempo_atual.pack(side="left")
        
        self.slider_tempo = ctk.CTkSlider(self.frame_tempo, from_=0, to=100, command=self.buscar_tempo_manual)
        self.slider_tempo.set(0)
        self.slider_tempo.pack(side="left", fill="x", expand=True, padx=10)
        
        self.lbl_tempo_total = ctk.CTkLabel(self.frame_tempo, text="00:00", width=40)
        self.lbl_tempo_total.pack(side="right")
        
        # 6. BOTÕES
        self.frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controles.pack(pady=5)
        
        self.btn_prev = ctk.CTkButton(self.frame_controles, text="⏮", width=40, command=self.acionar_voltar)
        self.btn_prev.pack(side="left", padx=5)
        
        self.btn_play = ctk.CTkButton(self.frame_controles, text="▶", width=40, command=self.player.tocar)
        self.btn_play.pack(side="left", padx=5)
        
        self.btn_pause = ctk.CTkButton(self.frame_controles, text="⏸", width=40, command=self.player.pausar)
        self.btn_pause.pack(side="left", padx=5)
        
        self.btn_stop = ctk.CTkButton(self.frame_controles, text="⏹", width=40, command=self.player.parar)
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_skip = ctk.CTkButton(self.frame_controles, text="⏭", width=40, command=self.acionar_avancar)
        self.btn_skip.pack(side="left", padx=5)
        
        # 7. VOLUME
        self.frame_vol = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vol.pack(pady=15)
        
        self.lbl_vol = ctk.CTkLabel(self.frame_vol, text="Volume")
        self.lbl_vol.pack(side="left", padx=5)
        
        self.slider_vol = ctk.CTkSlider(self.frame_vol, from_=0, to=1, command=self.mudar_volume)
        self.slider_vol.set(0.5)
        self.slider_vol.pack(side="left", padx=5)

        self.atualizar_relogio_gui()

    # --- FUNÇÕES ---
    def atualizar_capa(self):
        if self.player.faixa_atual:
            nome_base = os.path.splitext(self.player.faixa_atual)[0]
            caminhos_img = [nome_base + ".webp", nome_base + ".jpg", nome_base + ".png"]
            img_encontrada = None
            
            for caminho in caminhos_img:
                if os.path.exists(caminho):
                    img_encontrada = caminho
                    break
            
            if img_encontrada:
                img = Image.open(img_encontrada)
                ctk_img = ctk.CTkImage(img, size=(180, 180))
                self.lbl_capa.configure(image=ctk_img, text="")
            else:
                self.lbl_capa.configure(image="", text="🎵")

    def buscar_youtube(self, event=None):
        busca = self.entry_yt.get()
        if busca:
            self.lbl_status.configure(text="A processar e reproduzir... Aguarde!")
            self.update() 
            self.player.carregar_do_youtube(busca)
            self.lbl_status.configure(text=f"A tocar: {os.path.basename(self.player.faixa_atual)}")
            self.atualizar_playlist()
            self.atualizar_capa()
            self.entry_yt.delete(0, 'end')

    def mudar_volume(self, valor):
        pygame.mixer.music.set_volume(valor)
        self.player.volume = valor

    def buscar_tempo_manual(self, valor):
        if self.player.faixa_atual:
            self.player.buscar_posicao(valor)

    def atualizar_relogio_gui(self):
        if self.player.esta_tocando and not self.player.esta_pausado:
            tempo_ms = pygame.mixer.music.get_pos()
            tempo_atual = self.player.posicao_inicial_segundos + (tempo_ms / 1000)
            
            min_atual, seg_atual = int(tempo_atual // 60), int(tempo_atual % 60)
            self.lbl_tempo_atual.configure(text=f"{min_atual:02d}:{seg_atual:02d}")
            
            duracao = self.player.duracao_total
            if duracao > 0:
                min_tot, seg_tot = int(duracao // 60), int(duracao % 60)
                self.lbl_tempo_total.configure(text=f"{min_tot:02d}:{seg_tot:02d}")
                self.slider_tempo.configure(to=duracao)
                self.slider_tempo.set(tempo_atual)
                
        self.after(1000, self.atualizar_relogio_gui)

    def atualizar_playlist(self):
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()
        if os.path.exists("musica"):
            arquivos = [f for f in os.listdir("musica") if f.endswith(".mp3")]
            for arq in arquivos:
                btn = ctk.CTkButton(self.playlist_frame, text=arq, anchor="w", fg_color="transparent", 
                                    text_color="white", hover_color="#2ecc71", 
                                    command=lambda m=arq: self.tocar_da_playlist(m))
                btn.pack(fill="x", pady=2)

    def tocar_da_playlist(self, nome_musica):
        caminho = os.path.join("musica", nome_musica)
        self.player.parar()
        self.player.carregar_musica(caminho)
        self.player.tocar()
        self.lbl_status.configure(text=f"A tocar: {nome_musica}")
        self.atualizar_capa()

    def acionar_avancar(self):
        self.player.avancar_musica()
        if self.player.faixa_atual:
            self.lbl_status.configure(text=f"A tocar: {os.path.basename(self.player.faixa_atual)}")
            self.atualizar_capa()

    def acionar_voltar(self):
        self.player.voltar_musica()
        if self.player.faixa_atual:
            self.lbl_status.configure(text=f"A tocar: {os.path.basename(self.player.faixa_atual)}")
            self.atualizar_capa()

if __name__ == "__main__":
    app = InterfacePlayer()
    app.mainloop()