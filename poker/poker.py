#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------
import itertools
import collections

Card = collections.namedtuple('Card', 'rank suit true_rank')


def hand_rank(hand):
    u"""Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return 8, max(ranks)
    elif kind(4, ranks):
        return 7, kind(4, ranks), kind(1, ranks)
    elif kind(3, ranks) and kind(2, ranks):
        return 6, kind(3, ranks), kind(2, ranks)
    elif flush(hand):
        return 5, ranks
    elif bool(straight(ranks)):
        return 4, max(ranks)
    elif kind(3, ranks):
        return 3, kind(3, ranks), ranks
    elif two_pair(ranks):
        return 2, two_pair(ranks), ranks
    elif kind(2, ranks):
        return 1, kind(2, ranks), ranks
    else:
        return 0, ranks


def card_ranks(hand):
    u"""Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    list_ranks = list()
    for ch in itertools.chain.from_iterable(hand.split()):
        if ch in str(range(2, 10)):
            list_ranks.append(int(ch))
        elif ch == "T":
            list_ranks.append(10)
        elif ch == "J":
            list_ranks.append(11)
        elif ch == "Q":
            list_ranks.append(12)
        elif ch == "K":
            list_ranks.append(13)
        elif ch == "A":
            list_ranks.append(14)
    return sorted(list_ranks)


def flush(hand):
    u"""Возвращает True, если все карты одной масти"""
    set_of_suit = set()
    for ch in itertools.chain.from_iterable(hand.split()):
        if ch in ["C", "S", "H", "D"]:
            set_of_suit.add(ch)
    return True if len(set_of_suit) == 1 else False


def straight(ranks):
    u"""Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    for i in reversed(range(0, 3)):
        count = 0
        for n in range(0, 4):
            if ranks[i + n + 1] - ranks[i + n] == 1:
                count += 1
            else:
                break
        if count == 4:
            return True
    return False


def straight_hand(ranks):
    u"""Возвращает индекс начального элемента комбинации straight"""
    for i in reversed(range(0, len(ranks) - 4)):
        count = 0
        for n in range(0, 4):
            if ranks[i + n + 1] - ranks[i + n] == 1:
                count += 1
            else:
                break
        if count == 4:
            return i


def kind(n, ranks):
    u"""Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    i = 0
    count = 0
    while i < len(ranks):
        if i == len(ranks) - 1:
            return ranks[i] if n == 1 and ranks[i] != ranks[i - 1] else None
        elif ranks[i] == ranks[i + 1]:
            count += 1
            i += 1
        elif count == n - 1:
            return ranks[i]
        else:
            i += 1
            count = 0


def two_pair(ranks):
    u"""Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""  # возвращает два максимальных ранга
    items = list()
    for i in reversed(range(len(ranks))):
        if ranks[i] == ranks[i - 1]:
            items.append(ranks[i])
            i -= 1
        if len(items) == 2:
            return items[0], items[1]


def best_hand(hand):
    u"""Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    cards_objects = list()
    best_hand_list = list()
    for r, s in itertools.chain(hand.split()):
        true_rank = 0
        if r in str(range(2, 10)):
            true_rank = int(r)
        elif r == "T":
            true_rank = 10
        elif r == "J":
            true_rank = 11
        elif r == "Q":
            true_rank = 12
        elif r == "K":
            true_rank = 13
        elif r == "A":
            true_rank = 14
        cards_objects.append(Card(r, s, true_rank))
    cards_objects.sort(key=lambda c: c.true_rank)
    list_of_hand_rank = list(hand_rank(hand))
    if list_of_hand_rank[0] == 8 or list_of_hand_rank[0] == 4:  # straight
        suits = collections.Counter([card_obj.suit for card_obj in cards_objects])
        main_suit = max(suits.iteritems(), key=lambda t: t[1])
        start_of_straight = straight_hand([card_obj.true_rank for card_obj in cards_objects if
                                           card_obj.suit == main_suit[0]])
        for card in itertools.islice(cards_objects, start_of_straight, start_of_straight + 5):
            best_hand_list.append(card.rank + card.suit)
    if list_of_hand_rank[0] == 7 or list_of_hand_rank[0] == 6:
        best_hand_list = [card_obj.rank + card_obj.suit for card_obj in cards_objects if
                          card_obj.true_rank == list_of_hand_rank[1] or
                          card_obj.true_rank == list_of_hand_rank[2]]
    if list_of_hand_rank[0] == 5:
        for card in itertools.islice(cards_objects, 2, 7):
            best_hand_list.append(card.rank + card.suit)
    if list_of_hand_rank[0] == 3:
        filter_list = filter(lambda x: x != list_of_hand_rank[1], list_of_hand_rank[2])
        best_hand_list = [card_obj.rank + card_obj.suit for card_obj in cards_objects if
                          card_obj.true_rank == list_of_hand_rank[1] or
                          card_obj.true_rank == filter_list[len(filter_list) - 1] or
                          card_obj.true_rank == filter_list[len(filter_list) - 2]]
    if list_of_hand_rank[0] == 2:
        max_rank = max(filter(lambda x: x != list_of_hand_rank[1][0]
                                    and x != list_of_hand_rank[1][1], list_of_hand_rank[2]))
        best_hand_list = [card_obj.rank + card_obj.suit for card_obj in cards_objects if
                          card_obj.true_rank == list_of_hand_rank[1][0] or
                          card_obj.true_rank == list_of_hand_rank[1][1] or card_obj.true_rank == max_rank]
    if list_of_hand_rank[0] == 1:
        filter_list = filter(lambda x: x != list_of_hand_rank[1], list_of_hand_rank[2])
        print filter_list
        best_hand_list = [card_obj.rank + card_obj.suit for card_obj in cards_objects if
                          card_obj.true_rank == list_of_hand_rank[1] or
                          card_obj.true_rank in filter_list[2:5]]
    if list_of_hand_rank[0] == 0:
        for card in itertools.islice(cards_objects, 2, 7):
            best_hand_list.append(card.rank + card.suit)
    return best_hand_list


def best_wild_hand(hand):
    u"""best_hand но с джокерами"""
    return


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS"))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S"))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H"))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


"""
def test_best_wild_hand():
    print "test_best_wild_hand..."
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()

"""
