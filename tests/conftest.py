# [IA] Claude Code – configuração dos testes (backend sem janela do matplotlib)
import matplotlib

# Backend sem janela: permite testar gráficos em qualquer ambiente.
matplotlib.use("Agg")
