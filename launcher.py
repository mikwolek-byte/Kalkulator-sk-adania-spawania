"""Windows single-file entry point for the local Streamlit application."""
import multiprocessing
from pathlib import Path
import socket
import sys

def main():
    multiprocessing.freeze_support()
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8',errors='replace')
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
    sys.path.insert(0,str(root))
    smoke='--smoke-test' in sys.argv
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    if smoke:port=8501
    from streamlit.web import cli
    sys.argv=['streamlit','run',str(root/'app.py'),
              '--server.address=127.0.0.1',f'--server.port={port}',
              '--server.headless='+str(smoke).lower(),
              '--global.developmentMode=false',
              '--browser.gatherUsageStats=false','--server.fileWatcherType=none']
    print('Kalkulator Zekon — zamknij to okno, aby zakończyć program.')
    cli.main()

if __name__=='__main__':main()
