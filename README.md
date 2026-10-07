#Player de Música em Python

Um player de áudio com interface gráfica construído em Python. O sistema gerencia a reprodução de arquivos `.mp3` locais e integra-se de forma transparente com o YouTube para pesquisar, baixar e converter músicas automaticamente, incluindo a extração e exibição da capa do álbum.

## Funcionalidades
* **Interface Moderna:** Design em "Dark Mode" desenvolvido com CustomTkinter.
* **Integração YouTube:** Pesquisa e download de áudio diretamente da interface.
* **Capas de Álbum (Thumbnails):** Extração e exibição automática da arte associada ao áudio.
* **Controles de Reprodução:** Play, Pause, Stop, Anterior, Seguinte e controle de volume deslizante.
* **Barra de Progresso:** Atualização em tempo real com suporte a saltos (seek) na faixa atual.
* **Playlist Dinâmica:** Lista rolável que mapeia arquivos locais e permite reprodução com um clique.

## 🛠️ Stack Tecnológica
* **Python 3**
* **CustomTkinter:** Interface gráfica (GUI).
* **Pygame:** Motor de processamento e reprodução de áudio.
* **yt-dlp:** Extração de dados e mídia do YouTube.
* **Pillow (PIL):** Processamento e manipulação de imagens.
* **FFmpeg:** Conversão e pós-processamento de áudio.

## ⚙️ Como Executar

1. **Instale o FFmpeg** no seu sistema (obrigatório para a conversão de áudio do YouTube).
   * No Windows (via PowerShell): 
     ```bash
     winget install ffmpeg
     ```

2. **Instale as dependências do Python:**
   ```bash
   pip install pygame yt-dlp customtkinter Pillow
