extends CharacterBody2D


const SPEED = 300.0
const JUMP_VELOCITY = -400.0
var player = null

func _hitbox_enter(body):
	if body is CharacterBody2D:
		if body.has_method("takeDamage"):
			player = body
func _hitbox_exited(body):
	if body is CharacterBody2D:
		if body.has_method("takeDamage"):
			player = null

func _physics_process(delta: float) -> void:
	if player != null:
		randomize()
		var random_int := randi_range(6, 10)
		player.takeDamage(random_int)
