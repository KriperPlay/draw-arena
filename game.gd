extends Node2D

const Enemy = preload("res://enemy.tscn")

var enemy_count:int = 0
var count_volna_enemy:int = 5
var tm:bool = true
var next_volna:bool = true

@onready var spawnpoint1 = $SpawnPoint.position
@onready var spawnpoint2 = $SpawnPoint2.position
@onready var spawnpoint3 = $SpawnPoint3.position
@onready var spawnpoint4 = $SpawnPoint4.position

var spawn_number_use = 1
func _ready() -> void:
	pass

func spawn_enemy(pos: Vector2):
	var enemy = Enemy.instantiate()
	enemy.position = pos
	add_child(enemy)
	enemy_count += 1

func volna(count: int):
	if tm:
		randomize()
		var rand_enemy_count_spawn = randi_range(1,3)
		
		tm = false
		next_volna = false
		for i in range(count+rand_enemy_count_spawn):
			match spawn_number_use:
				1:
					spawn_enemy(spawnpoint1 + Vector2(randi_range(-500,500), randi_range(-500,500)))
					await get_tree().create_timer(1).timeout
					spawn_number_use += 1
				2:
					spawn_enemy(spawnpoint2 + Vector2(randi_range(-500,500), randi_range(-500,500)))
					await get_tree().create_timer(1).timeout
					spawn_number_use += 1
				3:
					spawn_enemy(spawnpoint3 + Vector2(randi_range(-500,500), randi_range(-500,500)))
					await get_tree().create_timer(1).timeout
					spawn_number_use += 1
				4:
					spawn_enemy(spawnpoint4 + Vector2(randi_range(-500,500), randi_range(-500,500)))
					await get_tree().create_timer(1).timeout
					spawn_number_use = 1
				_:
					spawn_number_use = 1
		await get_tree().create_timer(10).timeout
		count_volna_enemy += 3
		tm = true
	

func _process(delta: float) -> void:
	$CanvasLayer/enemy_count.text = str("Enemy: ",enemy_count)
	if enemy_count <= 0:
		next_volna = true
	
	if next_volna:
		volna(count_volna_enemy)
