import pygame
import os
import yt_dlp
import customtkinter as ctk

class PlayerDeMusica:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.faixa_atual = None
        self.esta_tocando = False
        self.esta_pausado = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)

    def carregar_musica(self, caminho_da_musica):
        if os.path.exists(caminho_da_musica):
            self.faixa_atual = caminho_da_musica
            pygame.mixer.music.load(self.faixa_atual)

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
        if self.faixa_atual is None:
            return
        pygame.mixer.music.play()
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

    def obter_tempo_atual(self):
        if self.esta_tocando:
            tempo_ms = pygame.mixer.music.get_pos()
            if tempo_ms > 0:
                seg_totais = tempo_ms // 1000
                return f"{seg_totais // 60:02d}:{seg_totais % 60:02d}"
        return "00:00"

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

    # NOVO MOTOR: Voltar música
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

# ==========================================
# INTERFACE GRÁFICA COMPLETA
# ==========================================
class InterfacePlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.player = PlayerDeMusica()
        
        self.title("🎵 Player de Música")
        self.geometry("550x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # 1. BARRA DE PESQUISA YOUTUBE
        self.frame_yt = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_yt.pack(pady=15, fill="x", padx=20)
        
        self.entry_yt = ctk.CTkEntry(self.frame_yt, placeholder_text="Buscar música no YouTube...")
        self.entry_yt.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_yt = ctk.CTkButton(self.frame_yt, text="Baixar", width=80, command=self.buscar_youtube)
        self.btn_yt.pack(side="right")
        
        # 2. PLAYLIST (Lista de músicas)
        self.lbl_playlist = ctk.CTkLabel(self, text="Músicas Locais:", font=("Arial", 14, "bold"))
        self.lbl_playlist.pack(anchor="w", padx=20)
        
        self.playlist_frame = ctk.CTkScrollableFrame(self, height=150)
        self.playlist_frame.pack(pady=5, fill="both", expand=True, padx=20)
        self.atualizar_playlist()
        
        # 3. STATUS DA MÚSICA
        self.lbl_status = ctk.CTkLabel(self, text="Player Pronto", font=("Arial", 14))
        self.lbl_status.pack(pady=10)
        
        # 4. BOTÕES DE CONTROLO (⏮, ▶, ⏸, ⏹, ⏭)
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
        
        # 5. CONTROLO DE VOLUME (Slider)
        self.frame_vol = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vol.pack(pady=15)
        
        self.lbl_vol = ctk.CTkLabel(self.frame_vol, text="Volume")
        self.lbl_vol.pack(side="left", padx=5)
        
        self.slider_vol = ctk.CTkSlider(self.frame_vol, from_=0, to=1, command=self.mudar_volume)
        self.slider_vol.set(0.5) # Começa nos 50%
        self.slider_vol.pack(side="left", padx=5)

    # --- Funções que conectam a interface ao motor ---
    
    def buscar_youtube(self):
        busca = self.entry_yt.get()
        if busca:
            self.lbl_status.configure(text="A descarregar... Aguarde! (A janela pode congelar uns segundos)")
            self.update() # Força a tela a atualizar antes de começar o download
            
            self.player.carregar_do_youtube(busca)
            
            self.lbl_status.configure(text="Download concluído! A tocar...")
            self.atualizar_playlist()
            self.entry_yt.delete(0, 'end')

    def mudar_volume(self, valor):
        pygame.mixer.music.set_volume(valor)
        self.player.volume = valor

    def atualizar_playlist(self):
        # Limpa as músicas antigas da tela
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()
            
        if os.path.exists("musica"):
            arquivos = [f for f in os.listdir("musica") if f.endswith(".mp3")]
            for arq in arquivos:
                # Cria um botão invisível para cada música (para poderes clicar nela)
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

    def acionar_avancar(self):
        self.player.avancar_musica()
        if self.player.faixa_atual:
            self.lbl_status.configure(text=f"A tocar: {os.path.basename(self.player.faixa_atual)}")

    def acionar_voltar(self):
        self.player.voltar_musica()
        if self.player.faixa_atual:
            self.lbl_status.configure(text=f"A tocar: {os.path.basename(self.player.faixa_atual)}")

if __name__ == "__main__":
    app = InterfacePlayer()
    app.mainloop()