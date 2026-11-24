extends CharacterBody2D

@onready var nav_agent: NavigationAgent2D = $NavigationAgent2D

var health = 100
var SPEED = 300.0
const JUMP_VELOCITY = -400.0
var player = null
var playerTargetMove = null

var lazer_active:bool = false
var tm:bool = true

func GetAttack(damage: int):
	health -= damage

func _hitbox_enter(body):
	if body is CharacterBody2D:
		if body.has_method("takeDamage"):
			player = body
func _hitbox_exited(body):
	if body is CharacterBody2D:
		if body.has_method("takeDamage"):
			player = null

func _ready() -> void:
	await get_tree().physics_frame
	playerTargetMove = get_tree().get_first_node_in_group("PLAYER")

func lazer():
	if tm:
		tm = false
		lazer_active = false
		$lazer.visible = false
		await get_tree().create_timer(1.5).timeout
		lazer_active = true
		$lazer.visible = true
		$AnimationPlayer2.play("Lazer")
		await get_tree().create_timer(1.5).timeout
		tm = true

func _physics_process(delta: float) -> void:
	lazer()
	$HealthBar.size = Vector2(health, 10)
	
	if health < 50:
		SPEED = 150.0
		$HealthBar.color = Color("#fd8d91")
	else:
		SPEED = 300.0
		$HealthBar.color = Color("#fa5567")
		
	if player != null && lazer_active:
		randomize()
		var random_int := randi_range(10, 20)
		player.takeDamage(random_int)
	
	if playerTargetMove != null and playerTargetMove.has_method("get_my_pos"):
		var target_pos = playerTargetMove.get_my_pos()
		nav_agent.target_position = target_pos
		var target_pos2 = nav_agent.get_next_path_position()
		var direction = global_position.direction_to(target_pos2)
		velocity = direction * SPEED
		move_and_slide()
