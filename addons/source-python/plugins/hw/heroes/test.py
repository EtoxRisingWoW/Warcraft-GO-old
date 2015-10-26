from hw.entities import Hero, Skill


class TestHero1(Hero):
    name = 'Test Hero'


@TestHero1.skill
class TestSkill(Skill):
    name = 'Test Skill'

    def player_spawn(self, **eargs):
        print('player spawned')
