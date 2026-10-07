import pygame
import os
import yt_dlp

class PlayerDeMusica:
    """
    Classe responsável por gerenciar a reprodução de ficheiros de áudio locais
    e a integração com downloads do YouTube para construção de biblioteca.
    """
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.faixa_atual = None
        self.esta_tocando = False
        self.esta_pausado = False
        self.volume = 0.5  # Começa em 50%
        
        pygame.mixer.music.set_volume(self.volume)

    def aumentar_volume(self):
        """Aumenta o volume em 10% até o máximo de 100%."""
        if self.volume < 1.0:
            self.volume = round(self.volume + 0.1, 1)
            pygame.mixer.music.set_volume(self.volume)
            print(f"\n[VOLUME] 🔊 Aumentado para {int(self.volume * 100)}%")
        else:
            print("\n[VOLUME] ⚠️ Já está no máximo (100%)")

    def diminuir_volume(self):
        """Diminui o volume em 10% até o mínimo (mudo)."""
        if self.volume > 0.0:
            self.volume = round(self.volume - 0.1, 1)
            pygame.mixer.music.set_volume(self.volume)
            print(f"\n[VOLUME] 🔉 Diminuído para {int(self.volume * 100)}%")
        else:
            print("\n[VOLUME] 🔇 Já está mudo (0%)")

    def carregar_musica(self, caminho_da_musica):
        if os.path.exists(caminho_da_musica):
            self.faixa_atual = caminho_da_musica
            pygame.mixer.music.load(self.faixa_atual)
            print(f"\n[INFO] Faixa carregada: {self.faixa_atual}")
        else:
            print(f"\n[ERRO] Ficheiro não encontrado no caminho: '{caminho_da_musica}'")

    def carregar_do_youtube(self, busca):
        pasta_destino = "musica"
        
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        self.parar()
        try:
            pygame.mixer.music.unload()
        except AttributeError:
            pass 
        
        print(f"\n[DOWNLOAD] A pesquisar '{busca}' no YouTube... (Isto pode demorar alguns segundos)")
        
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
            else:
                print("\n[ERRO] O ficheiro de áudio não foi encontrado após o download.")
        except Exception as e:
            print(f"\n[ERRO] Falha na integração com o YouTube: {e}")

    def tocar(self):
        if self.faixa_atual is None:
            print("\n[AVISO] Nenhuma faixa carregada no player.")
            return
        
        pygame.mixer.music.play()
        self.esta_tocando = True
        self.esta_pausado = False
        print(f"\n[PLAY] Reproduzindo: {self.faixa_atual}")

    def pausar(self):
        if self.esta_tocando and not self.esta_pausado:
            pygame.mixer.music.pause()
            self.esta_pausado = True
            print("\n[PAUSE] Reprodução pausada.")

    def retomar(self):
        if self.esta_pausado:
            pygame.mixer.music.unpause()
            self.esta_pausado = False
            print("\n[PLAY] Reprodução retomada.")

    def parar(self):
        pygame.mixer.music.stop()
        self.esta_tocando = False
        self.esta_pausado = False
        print("\n[STOP] Reprodução interrompida.")


def menu_principal():
    player = PlayerDeMusica()
    pasta_padrao = "musica" 
    
    while True:
        status = "Parado"
        if player.esta_pausado:
            status = "Pausado"
        elif player.esta_tocando:
            status = "Tocando"
            
        print("\n" + "="*45)
        # O cabeçalho agora mostra o volume dinamicamente (multiplicado por 100 para ficar de 0 a 100%)
        print(f"🎵 TERMINAL PLAYER - [{status}] | Vol: {int(player.volume * 100)}%")
        if player.faixa_atual:
            print(f"Faixa: {player.faixa_atual}")
        print("="*45)
        
        print("1 - Escolher música local")
        print("2 - Buscar no YouTube 🌐")
        print("3 - Play")
        print("4 - Pause")
        print("5 - Retomar")
        print("6 - Stop")
        print("7 - Aumentar Volume (+)")
        print("8 - Diminuir Volume (-)")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            if not os.path.exists(pasta_padrao):
                print(f"\n[ERRO] A pasta '{pasta_padrao}' não existe. Crie a pasta e coloque os seus MP3 nela.")
                continue

            arquivos_mp3 = [arquivo for arquivo in os.listdir(pasta_padrao) if arquivo.endswith(".mp3")]

            if not arquivos_mp3:
                print(f"\n[AVISO] Nenhuma música encontrada na pasta '{pasta_padrao}'.")
                continue

            print("\n=== Biblioteca de Músicas ===")
            for indice, arquivo in enumerate(arquivos_mp3):
                print(f"{indice + 1} - {arquivo}")
            print("0 - Cancelar e voltar")

            escolha_musica = input("\nDigite o número da música: ")

            if escolha_musica.isdigit():
                numero_escolhido = int(escolha_musica)
                
                if numero_escolhido == 0:
                    continue 
                elif 1 <= numero_escolhido <= len(arquivos_mp3):
                    nome_arquivo = arquivos_mp3[numero_escolhido - 1]
                    caminho_completo = os.path.join(pasta_padrao, nome_arquivo)
                    player.carregar_musica(caminho_completo)
                    player.tocar()
                else:
                    print("\n[ERRO] Número fora da lista.")
            else:
                print("\n[ERRO] Por favor, digite apenas números.")

        elif opcao == "2":
            busca = input("\nDigite o nome da música ou artista: ")
            if busca.strip():
                player.carregar_do_youtube(busca)
            else:
                print("\n[AVISO] A busca não pode estar vazia.")

        elif opcao == "3":
            player.tocar()
        elif opcao == "4":
            player.pausar()
        elif opcao == "5":
            player.retomar()
        elif opcao == "6":
            player.parar()
        elif opcao == "7":
            player.aumentar_volume()
        elif opcao == "8":
            player.diminuir_volume()
        elif opcao == "0":
            player.parar()
            print("\nA encerrar a aplicação...")
            break
        else:
            print("\n[ERRO] Opção inválida.")

if __name__ == "__main__":
    menu_principal()
    