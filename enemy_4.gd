extends CharacterBody2D

@onready var nav_agent: NavigationAgent2D = $NavigationAgent2D

var health = 500
var SPEED = 300.0
const JUMP_VELOCITY = -400.0
var player = null
var playerTargetMove = null
var rage = true

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

func rage_mode():
	if rage:
		rage = false
		SPEED = 500.0
		await get_tree().create_timer(4).timeout
		SPEED = 300.0
		await get_tree().create_timer(4).timeout
		rage = true

func _physics_process(delta: float) -> void:
	rage_mode()
	
	$HealthBar.size = Vector2(health, 20)
		
	if player != null:
		randomize()
		var random_int := randi_range(6, 10)
		player.takeDamage(random_int)
	
	if playerTargetMove != null and playerTargetMove.has_method("get_my_pos"):
		var target_pos = playerTargetMove.get_my_pos()
		nav_agent.target_position = target_pos
		var target_pos2 = nav_agent.get_next_path_position()
		var direction = global_position.direction_to(target_pos2)
		velocity = direction * SPEED
		move_and_slide()
