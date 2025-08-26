import flet as ft
import random
import asyncio
from collections import deque

class EightPuzzleApp:
    def __init__(self, page: ft.Page):
        # Configurações da interface
        self.page = page
        self.page.title = "Quebra-Cabeça Deslizante (8 Peças)"
        self.page.window_width = 400
        self.page.window_height = 580
        self.page.bgcolor = "#F5F5F5"
        self.page.padding = 10
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        # Estado inicial resolvido (1-8 + espaço vazio)
        self.state = [1, 2, 3, 4, 5, 6, 7, 8, None]
        self.goal_state = self.state[:]

        # Grade 3x3 fixa com tiles quadrados
        self.grid = ft.GridView(
            runs_count=3,
            max_extent=100,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
            width=315,
            height=315,
            padding=5,
        )

        # Botões de controle
        self.shuffle_button = ft.ElevatedButton(
            "Embaralhar",
            on_click=self.on_shuffle,
            style=ft.ButtonStyle(
                bgcolor="#00796b",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=10,
            ),
        )
        self.solve_button = ft.ElevatedButton(
            "Resolver",
            on_click=self.on_solve,
            style=ft.ButtonStyle(
                bgcolor="#004d40",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=10,
            ),
        )
        self.reset_button = ft.ElevatedButton(
            "Resetar",
            on_click=self.on_reset,
            style=ft.ButtonStyle(
                bgcolor="#d32f2f",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=10,
            ),
        )

        # Layout principal
        self.controls = ft.Column(
            [
                ft.Container(
                    width=315,
                    height=80,
                    bgcolor="#FFFFFF",
                    border_radius=8,
                    content=ft.Image(
                        src="ifto.png",
                        width=140,
                        height=70,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "Quebra-Cabeça 8 Peças",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#004d40",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Sistemas Inteligentes de Apoio à Decisão",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="#004d40",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Integrantes: Adelson Teodoro, Arthur Duarte, Leandro Milhomem, Keyton Bessa e Savio Vitor",
                    size=12,
                    color="#004d40",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=self.grid,
                    bgcolor="#FFFFFF",
                    border_radius=8,
                    padding=5,
                    shadow=ft.BoxShadow(
                        blur_radius=6,
                        spread_radius=1,
                        color="#B0BEC5",
                    ),
                ),
                ft.Row(
                    [self.shuffle_button, self.solve_button, self.reset_button],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            width=350,
        )

        self.page.add(self.controls)
        self.build_grid()

    def build_grid(self):
        # Atualiza visualmente o grid com base no estado atual
        self.grid.controls.clear()
        for val in self.state:
            if val is None:
                tile = ft.Container(
                    bgcolor="#E0E0E0",
                    border_radius=5,
                    border=ft.border.all(1, "#B0BEC5"),
                    width=100,
                    height=100,
                )
            else:
                tile = ft.Container(
                    content=ft.Text(
                        str(val),
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    bgcolor="#00796b",
                    alignment=ft.alignment.center,
                    border_radius=5,
                    border=ft.border.all(1, "#004d40"),
                    width=100,
                    height=100,
                    ink=True,
                    on_click=lambda e, v=val: self.move_tile(v),  # Associa clique à peça
                )
            self.grid.controls.append(tile)
        self.page.update()

    def move_tile(self, val):
        # Move uma peça se estiver ao lado do espaço vazio
        i = self.state.index(val)
        j = self.state.index(None)
        xi, yi = divmod(i, 3)
        xj, yj = divmod(j, 3)
        if abs(xi - xj) + abs(yi - yj) == 1:
            self.state[i], self.state[j] = self.state[j], self.state[i]
            self.build_grid()

    def on_shuffle(self, e):
        # Embaralha com movimentos válidos (mantém solução possível)
        for _ in range(50):
            neighbors = self.get_neighbors(self.state)
            self.state = random.choice(neighbors)
        self.build_grid()

    def on_reset(self, e):
        # Retorna ao estado resolvido
        self.state = self.goal_state[:]
        self.build_grid()

    def on_solve(self, e):
        # Informa o usuário e inicia a resolução
        self.page.snack_bar = ft.SnackBar(ft.Text("Resolvendo..."), open=True)
        self.page.update()
        self.page.run_task(self.solve_puzzle)  # Executa tarefa assíncrona

    async def solve_puzzle(self):
        # Executa a busca e anima os passos até a solução
        path = self.bfs(self.state, self.goal_state)
        if path:
            for step in path[1:]:
                self.state = step
                self.build_grid()
                await asyncio.sleep(0.3)  # Delay para animação
            self.page.snack_bar = ft.SnackBar(ft.Text("Resolvido!"), open=True)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Não foi possível resolver."), open=True)
        self.page.update()

    def bfs(self, start, goal):
        # Busca em largura (BFS) para encontrar o caminho até o estado resolvido
        q = deque([(start, [])])
        visited = set()
        while q:
            state, path = q.popleft()
            if tuple(state) in visited:
                continue
            visited.add(tuple(state))
            path = path + [state]
            if state == goal:
                return path  # Caminho encontrado
            for neighbor in self.get_neighbors(state):
                if tuple(neighbor) not in visited:
                    q.append((neighbor, path))
        return None  # Sem solução

    def get_neighbors(self, state):
        # Gera estados vizinhos (movimentos possíveis do espaço vazio)
        neighbors = []
        i = state.index(None)
        x, y = divmod(i, 3)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esq, dir
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                j = nx * 3 + ny
                new_state = state[:]
                new_state[i], new_state[j] = new_state[j], new_state[i]
                neighbors.append(new_state)
        return neighbors

def main(page: ft.Page):
    EightPuzzleApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
