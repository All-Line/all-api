import io
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import requests
from decouple import config as env


def generate_social_graph(data):
    all_words = [word for subset in data for word in subset]
    word_freq = Counter(all_words)

    G = nx.Graph()

    for word, freq in word_freq.items():
        if freq > 1:
            G.add_node(word, size=freq)

    for subset in data:
        for word1 in subset:
            for word2 in subset:
                if word1 != word2 and word1 in G.nodes() and word2 in G.nodes():
                    if not G.has_edge(word1, word2):
                        G.add_edge(word1, word2, weight=1)

    return G


def draw_social_graph(graph, color):
    pos = nx.spring_layout(graph)
    node_size = [graph.nodes[n]["size"] ** 4 for n in graph.nodes()]
    edge_width = [graph[u][v]["weight"] * 0.4 for u, v in graph.edges()]
    node_font_size = {n: graph.nodes[n]["size"] for n in graph.nodes()}
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=node_size,
        node_color=color,
        edgecolors="#00000055",
        linewidths=1,
    )
    nx.draw_networkx_edges(graph, pos, width=edge_width, alpha=0.1, edge_color=color)
    for node, (x, y) in pos.items():
        plt.text(x, y, node, fontsize=node_font_size[node], ha="center", va="center")
    plt.axis("off")
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=400)
    plt.clf()
    buffer.seek(0)

    return buffer


def get_tweets(query):
    url = f"https://twitter.com/i/api/graphql/zJaDsyzhXP2rS8MamXX86Q/SearchTimeline?variables=%7B%22rawQuery%22%3A%22{query}%22%2C%22count%22%3A20%2C%22querySource%22%3A%22spelling_expansion_revert_click%22%2C%22product%22%3A%22Top%22%7D&features=%7B%22rweb_tipjar_consumption_enabled%22%3Afalse%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D"  # noqa

    headers = {
        "X-Csrf-Token": env("CSRF_TWITTER"),
        "X-Client-Uuid": env("CLIENT_UUID_TWITTER"),
        "X-Client-Transaction-Id": env("CLIENT_TRANSACTION_ID_TWITTER"),
        "Cookie": env("COOKIE_TWITTER"),
        "Authorization": f"Bearer {env('AUTHORIZATION_TWITTER')}",
        "Accept": "*/*",
    }
    response = requests.request("GET", url, data="", headers=headers)

    json_response = response.json()

    entries = json_response["data"]["search_by_raw_query"]["search_timeline"][
        "timeline"
    ]["instructions"][0]["entries"]

    return [
        entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"][
            "full_text"
        ]
        for entry in entries
        if "itemContent" in entry["content"]
        and "tweet_results" in entry["content"]["itemContent"]
        and "result" in entry["content"]["itemContent"]["tweet_results"]
        and "legacy" in entry["content"]["itemContent"]["tweet_results"]["result"]
        and "full_text"
        in entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]
    ]


def get_social_network_image(param, providers, color="#66c2a5"):
    flows = {
        "Twitter": _twitter_provider_flow,
    }
    data = []
    for provider in list(set(providers)):
        if provider in flows:
            data.append(flows[provider](param))

    graph = generate_social_graph(data)

    graph_bytes = draw_social_graph(graph, color)

    return graph_bytes


def _twitter_provider_flow(param):
    twitter_data = get_tweets(param)

    data = []
    for tweet in twitter_data:
        tweet = tweet.lower()
        data += [
            word
            for word in tweet.split()
            if "http" not in word and len(word) > 4 and param not in word
        ]

    return data
