import pytest
import aporganizer

TEST_CREATOR = "0123456789"
TEST_CREATOR_2 = "987543210"
TEST_YAML = b"name: Testing"
TEST_YAML_2 = b"name: Testing\r\ndata: asdf"
TEST_SLOT_NAME = "Testing"
TEST_GAME = "Bingly 3"
TEST_APWORLD = b"asdf"


@pytest.fixture()
def organizer():
    return aporganizer.APOrganizer(":memory:")


def test_read_slot_name():
    slot_name = aporganizer.read_slot_name(TEST_YAML)
    assert slot_name == TEST_SLOT_NAME


@pytest.mark.parametrize(
    "data",
    [
        b"!*$(^&%(#*",  # non-yaml data
        b"mame: Testing",  # "name" key not in yaml
    ],
)
def test_read_slot_name_bad(data):
    with pytest.raises(aporganizer.InvalidYamlException):
        aporganizer.read_slot_name(data)


def test_add_yaml(organizer):
    yaml = organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    assert yaml.slot_name == TEST_SLOT_NAME


def test_add_yaml_overwrite(organizer):
    organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    organizer.add_yaml(TEST_CREATOR, TEST_YAML_2)
    yamls = list(organizer.get_yamls())
    assert len(yamls) == 1
    assert yamls[0].data == TEST_YAML_2


def test_add_yaml_overwrite_bad(organizer):
    organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    with pytest.raises(aporganizer.AlreadyExistsException):
        organizer.add_yaml(TEST_CREATOR_2, TEST_YAML)


def test_add_yaml_toobig(organizer):
    huge_yaml = b" " * 600000  # weirdly large yaml
    with pytest.raises(aporganizer.FileTooBigException):
        organizer.add_yaml(TEST_CREATOR_2, huge_yaml)


def test_get_yamls_none(organizer):
    assert len(list(organizer.get_yamls())) == 0


def test_get_yamls_one(organizer):
    yaml = organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    yamls = list(organizer.get_yamls())
    assert len(yamls) == 1
    assert yaml.yaml_id == yamls[0].yaml_id
    assert yaml.slot_name == yamls[0].slot_name
    assert yaml.creator_id == yamls[0].creator_id
    assert yaml.data == yamls[0].data


def test_get_yamls_one_nodata(organizer):
    organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    yamls = list(organizer.get_yamls(get_data=False))
    assert yamls[0].data == None


def test_delete_yaml(organizer):
    yaml = organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    organizer.delete_yaml(yaml.slot_name)
    assert len(list(organizer.get_yamls())) == 0


def test_delete_yaml_nonexistent(organizer):
    with pytest.raises(aporganizer.NotExistsException):
        organizer.delete_yaml("slot")


def test_add_apworld(organizer):
    apworld = organizer.add_apworld(TEST_CREATOR, TEST_GAME, TEST_APWORLD)
    assert apworld.apworld_id is not None
    assert apworld.creator_id == TEST_CREATOR
    assert apworld.game_name == TEST_GAME
    assert apworld.data == TEST_APWORLD


def test_add_apworld_toobig(organizer):
    huge_apworld = b" " * 1100000  # weirdly large yaml
    with pytest.raises(aporganizer.FileTooBigException):
        organizer.add_apworld(TEST_CREATOR, TEST_GAME, huge_apworld)


def test_get_apworlds_none(organizer):
    assert len(list(organizer.get_apworlds())) == 0


def test_get_apworlds_one(organizer):
    apworld = organizer.add_apworld(TEST_CREATOR, TEST_GAME, TEST_APWORLD)
    apworlds = list(organizer.get_apworlds())
    assert len(apworlds) == 1
    assert apworld.apworld_id == apworlds[0].apworld_id
    assert apworld.creator_id == apworlds[0].creator_id
    assert apworld.game_name == apworlds[0].game_name
    assert apworld.data == apworlds[0].data


def test_get_yamls_one_nodata(organizer):
    organizer.add_apworld(TEST_CREATOR, TEST_GAME, TEST_APWORLD)
    apworlds = list(organizer.get_apworlds(get_data=False))
    assert apworlds[0].data == None


def test_clear(organizer):
    organizer.add_yaml(TEST_CREATOR, TEST_YAML)
    organizer.add_apworld(TEST_CREATOR, TEST_GAME, TEST_APWORLD)
    organizer.clear()
    assert len(list(organizer.get_yamls())) == 0
    assert len(list(organizer.get_apworlds())) == 0
