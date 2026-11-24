extends CharacterBody2D

@onready var nav_agent: NavigationAgent2D = $NavigationAgent2D

const SPEED = 300.0
const JUMP_VELOCITY = -400.0
var player = null
var playerTargetMove = null

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


func _physics_process(delta: float) -> void:
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
