extends CharacterBody2D

var Hp: int = 100

var SPEED = 600
var USKORENIE = 1
var ATTACK = 10
var DEFENCE = 5

var dvizh: bool = false

func _physics_process(delta: float) -> void:
	$Camera2D/CanvasLayer/Attackvalue.text = str(ATTACK)
	$Camera2D/CanvasLayer/Defencevalue.text = str(DEFENCE)
	$Camera2D/CanvasLayer/Speedvalue.text = str(USKORENIE)
	
	$Camera2D/CanvasLayer/HealthBar.size = Vector2(Hp*3, 64)
	$Camera2D/CanvasLayer/Label.text = str(Hp)
	
	if Hp > 100:
		Hp = 100
	
	var direction := Input.get_vector("a", "d", "w", "s")
	velocity = direction * SPEED * USKORENIE
	move_and_slide()
