extends CharacterBody2D

var Hp: int = 100

var SPEED = 600
var USKORENIE = 1
var ATTACK = 10
var DEFENCE = 5

var death:bool = false

var tm:bool = true

func _takeDamage(damage: int):
	if tm:
		tm = false
		$Hp.play()
		Hp -= damage
		await get_tree().create_timer(0.69).timeout
		tm = true

func _pause():
	get_tree().paused = !get_tree().paused

func _physics_process(delta: float) -> void:
	#_takeDamage(10)
	
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
	
	var direction := Input.get_vector("a", "d", "w", "s")
	velocity = direction * SPEED * USKORENIE
	move_and_slide()
