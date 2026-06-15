import json

import pytest

import update


def make_item(title, video_id):
    return {
        'snippet': {'title': title},
        'id': {'videoId': video_id},
    }


def test_find_live_streams_matches_target_titles():
    nasa_title = update.TARGET_TITLES[0]
    sen_title = update.TARGET_TITLES[-1]

    items = [
        make_item(nasa_title, 'aaa'),
        make_item(sen_title, 'fO9e9jnhYK8'),
        make_item('Some unrelated live stream', 'zzz'),
    ]

    urls = update.find_live_streams(items)

    assert urls == [
        'https://www.youtube.com/watch?v=aaa',
        'https://www.youtube.com/watch?v=fO9e9jnhYK8',
    ]


def test_find_live_streams_ignores_non_matching_titles():
    items = [make_item('Random title', 'abc')]
    assert update.find_live_streams(items) == []


def test_find_live_streams_handles_missing_snippet():
    items = [{'id': {'videoId': 'abc'}}]
    assert update.find_live_streams(items) == []


def test_find_live_streams_empty_input_returns_none():
    assert update.find_live_streams([]) is None


def test_sen_title_is_present():
    assert any('Sen' in title for title in update.TARGET_TITLES)


def test_two_channel_ids_configured():
    assert update.NASA_CHANNEL_ID == [
        'UCLA_DiR1FfKNvjuUpBHmylQ',
        'UCkvW_7kp9LJrztmgA4q4bJQ',
    ]


def write_json(path, version, urls):
    path.write_text(json.dumps({
        'version': version,
        'links': {'25544': {'youtube': urls}},
    }), encoding='utf-8')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def test_update_json_writes_new_urls_and_bumps_version(tmp_path):
    f = tmp_path / 'live_streams.json'
    write_json(f, '17', ['https://www.youtube.com/watch?v=old'])

    new_urls = ['https://www.youtube.com/watch?v=new']
    update.update_json(str(f), new_urls)

    data = read_json(f)
    assert data['links']['25544']['youtube'] == new_urls
    assert data['version'] == '18'


def test_update_json_no_change_when_urls_already_present(tmp_path):
    f = tmp_path / 'live_streams.json'
    existing = ['https://www.youtube.com/watch?v=a', 'https://www.youtube.com/watch?v=b']
    write_json(f, '17', existing)

    # all new urls already exist -> no write, version stays
    update.update_json(str(f), ['https://www.youtube.com/watch?v=a'])

    data = read_json(f)
    assert data['version'] == '17'
    assert data['links']['25544']['youtube'] == existing


def test_update_json_missing_file_returns_none(tmp_path):
    missing = tmp_path / 'nope.json'
    assert update.update_json(str(missing), ['x']) is None