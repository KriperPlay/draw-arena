extends CharacterBody2D

var Hp: int = 100

const SPEED = 300.0
const JUMP_VELOCITY = -400.0
var dvizh: bool = false

func _physics_process(delta: float) -> void:
	$Camera2D/CanvasLayer/HealthBar.size = Vector2(Hp*3, 64)
	$Camera2D/CanvasLayer/Label.text = str(Hp)
	
	if Hp > 100:
		Hp = 100
	
	var direction := Input.get_vector("a", "d", "w", "s")
	velocity = direction * SPEED
	move_and_slide()
