forever stopall
forever start Server.js
forever start ResourceManager/index.js
cd FingerPhasePredictor
forever start -c python3 main.py
cd ..