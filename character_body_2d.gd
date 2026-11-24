extends CharacterBody2D

var image: Image
var draw_texture: ImageTexture

var Hp: int = 100

var SPEED = 600
var USKORENIE = 1
var ATTACK = 5
var DEFENCE = 5
var PAUSED = false

var death:bool = false

var tm:bool = true
var tm2:bool = true

var target = []

func enemy_entered(body):
	if body is CharacterBody2D:
		if body.has_method("GetAttack"):
			target.append(body)
func enemy_exited(body):
	if body is CharacterBody2D:
		if body.has_method("GetAttack"):
			target.erase(body)

func takeDamage(damage: int):
	if tm:
		tm = false
		$Hp.play()
		Hp -= damage / DEFENCE
		await get_tree().create_timer(0.69).timeout
		tm = true

func _pause():
	get_tree().paused = !get_tree().paused
	PAUSED = get_tree().paused 
	if PAUSED == true: $Camera2D/CanvasLayer/pause.show()
	else: $Camera2D/CanvasLayer/pause.hide()

func _ready() -> void:
	add_to_group("PLAYER")
	if FileAccess.file_exists("user://my_character.png"):
		image = Image.load_from_file("user://my_character.png")
		draw_texture = ImageTexture.create_from_image(image)
		$Sprite2D.texture = draw_texture

func get_my_pos() -> Vector2:
	return global_position

func Attack():
	if tm2:
		tm2 = false
		for i in target:
			i.GetAttack(ATTACK)
			print(i.health)
			break
		await get_tree().create_timer(0.2).timeout
		tm2 = true

func _physics_process(delta: float) -> void:
	if target != null:
		Attack()
	
	$Camera2D/CanvasLayer/Attackvalue.text = str(ATTACK)
	$Camera2D/CanvasLayer/Defencevalue.text = str(DEFENCE)
	$Camera2D/CanvasLayer/Speedvalue.text = str(USKORENIE)
	
	$Camera2D/CanvasLayer/HealthBar.size = Vector2(Hp*3, 64)
	$Camera2D/CanvasLayer/Label.text = str(Hp)
	
	if Hp > 100:
		Hp = 100
	if Hp <= 0:
		Hp = 0
		death = true
	
	var direction := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = direction * SPEED * USKORENIE
	move_and_slide()
