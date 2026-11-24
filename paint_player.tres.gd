extends Sprite2D

var image: Image
var draw_texture: ImageTexture

var brush_size := 10
var brush_color := Color.BLACK
var last_pos := Vector2i(-1, -1)

# --- Счётчики нажатий по цветам ---
# Сюда вешай свои переменные статов, как хочешь — я просто считаю нажатия
var black_presses := 0
var red_presses := 0
var blue_presses := 0

func _ready():
	image = Image.create(500, 500, false, Image.FORMAT_RGBA8)
	image.fill(Color.TRANSPARENT)
	draw_texture = ImageTexture.create_from_image(image)
	self.texture = draw_texture

func _input(event):
	# Старт штриха — считаем нажатие
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_register_press()
	if event is InputEventScreenTouch and event.pressed:
		_register_press()

	# Рисование
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_LEFT:
		var local_pos = to_local(event.position)
		if centered:
			local_pos += Vector2(image.get_width(), image.get_height()) / 2.0
		var current = Vector2i(int(local_pos.x), int(local_pos.y))

		if brush_color == Color.BLACK or brush_color == Color.RED or brush_color == Color.BLUE:
			if last_pos.x >= 0:
				_draw_line_between(last_pos, current)
			else:
				_paint(current.x, current.y)

		last_pos = current
		draw_texture.update(image)

	if event is InputEventScreenDrag:
		var local_pos = to_local(event.position)
		if centered:
			local_pos += Vector2(image.get_width(), image.get_height()) / 2.0
		var current = Vector2i(int(local_pos.x), int(local_pos.y))
		if last_pos.x >= 0:
			_draw_line_between(last_pos, current)
		else:
			_paint(current.x, current.y)
		last_pos = current
		draw_texture.update(image)

	# Отпускание
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and not event.pressed:
		last_pos = Vector2i(-1, -1)
	if event is InputEventScreenTouch and not event.pressed:
		last_pos = Vector2i(-1, -1)

func _register_press() -> void:
	if brush_color == Color.BLACK:
		black_presses += 1
	elif brush_color == Color.RED:
		red_presses += 1
	elif brush_color == Color.BLUE:
		blue_presses += 1

func _unhandled_input(event):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			brush_size = min(brush_size + 1, 20)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			brush_size = max(brush_size - 1, 0)

func _draw_line_between(from: Vector2i, to: Vector2i):
	var steps = max(abs(to.x - from.x), abs(to.y - from.y))
	if steps == 0:
		_paint(to.x, to.y)
		return
	for i in range(steps + 1):
		var t = float(i) / float(steps)
		var px = int(lerp(from.x, to.x, t))
		var py = int(lerp(from.y, to.y, t))
		_paint(px, py)

func _paint(x: int, y: int):
	for dx in range(-brush_size, brush_size + 1):
		for dy in range(-brush_size, brush_size + 1):
			if dx * dx + dy * dy <= brush_size * brush_size:
				var px = x + dx
				var py = y + dy
				if px >= 0 and px < image.get_width() and py >= 0 and py < image.get_height():
					image.set_pixel(px, py, brush_color)

func save_character():
	image.save_png("user://my_character.png")
	# --- Здесь мапишь счётчики в свои статы, например: ---
	Global.ATTACK += red_presses
	Global.DEFENCE += blue_presses
	# Global.USKORENIE = 1.0 + black_presses * 0.05

func _on_play_pressed() -> void:
	save_character()
	await get_tree().create_timer(1).timeout
	get_tree().change_scene_to_file("res://game.tscn")

func _on_red_pressed() -> void:
	brush_color = Color.RED

func _on_black_pressed() -> void:
	brush_color = Color.BLACK

func _on_blue_pressed() -> void:
	brush_color = Color.BLUE
