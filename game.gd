extends Node2D

const Enemy = preload("res://enemy.tscn")
const Enemy2 = preload("res://Enemy2.tscn")
const Enemy3 = preload("res://Enemy3.tscn")
const Enemy_Boss = preload("res://EnemyBoss.tscn")

const Heal = preload("res://Heal.tscn")
var heal_count = 0;

var enemy_count:int = 0
var count_volna_enemy:int = 1
var tm:bool = true
var next_volna:bool = true


@onready var spawnpoint1 = $SpawnPoint.position
@onready var spawnpoint2 = $SpawnPoint2.position
@onready var spawnpoint3 = $SpawnPoint3.position
@onready var spawnpoint4 = $SpawnPoint4.position

var enemys = []

var spawn_number_use = 1
func _ready() -> void:
	pass

func spawn_enemy(pos: Vector2):
	randomize()
	var rand_enemy = randi_range(1,100)
	
	if rand_enemy <= 85 && rand_enemy >= 40:
		var enemy = Enemy.instantiate()
		enemy.position = pos
		add_child(enemy)
		enemy_count += 1
		enemys.append(enemy)
	elif rand_enemy < 40 && rand_enemy > 20:
		var enemy = Enemy3.instantiate()
		enemy.position = pos
		add_child(enemy)
		enemy_count += 1
		enemys.append(enemy)
	elif rand_enemy <= 20 && rand_enemy > 5:
		var enemy = Enemy2.instantiate()
		enemy.position = pos
		add_child(enemy)
		enemy_count += 1
		enemys.append(enemy)
	else:
		var enemy = Enemy_Boss.instantiate()
		enemy.position = pos
		add_child(enemy)
		enemy_count += 1
		enemys.append(enemy)

func volna(count: int):
	if tm:
		randomize()
		var rand_enemy_count_spawn = randi_range(1,3)
		
		tm = false
		next_volna = false
		
		$CanvasLayer/CD_Volna.visible = true
		$CanvasLayer/CD_Volna.text = "Волна начнется через 10 секунд"
		await get_tree().create_timer(10).timeout
		$CanvasLayer/CD_Volna.visible = false
		
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
		count_volna_enemy += 3
		await get_tree().create_timer(25).timeout
		tm = true
var tm2 = true
func DeathTp():
	if tm2:
		tm2 = false
		$CanvasLayer/Death/AnimationPlayer2.play("death")
		await get_tree().create_timer(1).timeout
		get_tree().change_scene_to_file("res://dead_frame.tscn")
		tm2 = true

var tm3:bool = true
func Heal_meth():
	if tm3:
		tm3 = true
		randomize()
		var heal = Heal.instantiate()
		heal.position = Vector2(randf_range(-2000.0,2000.0),randf_range(-2000.0,2000.0))
		add_child(heal)
		heal_count += 1
		await get_tree().create_timer(20).timeout
		heal_count = 0
		tm3 = false

func _process(delta: float) -> void:
	if heal_count < 4:
		Heal_meth()
	
	if $player.death:
		DeathTp()
	
	for i in enemys:
		if i.health == 0:
			i.queue_free()
			enemys.erase(i)
			enemy_count -= 1
	
	$CanvasLayer/enemy_count.text = str("Enemy: ",enemy_count)
	if enemy_count <= 0:
		next_volna = true
	
	if next_volna:
		volna(count_volna_enemy)
