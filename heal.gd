extends StaticBody2D


func _ready() -> void:
	pass

func heal_enter(body):
	if body is CharacterBody2D:
		if body.has_method("takeDamage"):
			body.Hp += 15
			queue_free()

func _process(delta: float) -> void:
	pass
