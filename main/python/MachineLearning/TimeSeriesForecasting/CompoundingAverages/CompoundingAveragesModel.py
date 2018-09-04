
import operator


# ========================================================
# ==========          Model Definition          ==========
# ========================================================


def model(data):
    # Split into training and test data
    length = len(data)
    split = round(length * 0.8)

    # Step through the predictions
    predictions = []
    print_summary_info = True
    start = 0
    while split < length:
        print("\n===== {} - {} =====\n".format(data[start][0], data[split][0]))
        data_train = data[start:split]
        data_test = data[split:]
        predictions.append(model_step(data_test, data_train, print_summary_info))
        start += 1
        split += 1

    # Iterate over our list and display outcomes
    print_predictions = False
    correct_predictions = 0
    list_predictions = []
    list_outcomes = []
    for item in predictions:
        prediction = item[0]
        actual = item[2]
        if prediction == actual:
            correct_predictions += 1
        else:
            if print_predictions:
                print("Predicted - {} - at {:4.2f} % - was actually - {}".format(prediction, item[1] * 100, actual))
                list_predictions.append(evaluate(prediction))
                list_outcomes.append(evaluate(actual))

    print()
    print("Correct predictions = {} / {} ({:4.2f} %)".format(correct_predictions, len(predictions), (correct_predictions / len(predictions)) * 100))
    return list_predictions, list_outcomes


def model_step(data_test, data_train, print_summary_info=False):
    length = len(data_train)
    print_detailed_info = True

    # prob_1, verdict_1, stag_1, incr_1, decr_1, trend_u1, trend_d1 = mill_avgerage(data_train, length, 0.99, print_detailed_info)
    prob_5, verdict_5, stag_5, incr_5, decr_5, trend_u5, trend_d5 = mill_avgerage(data_train, length, 0.95, print_detailed_info)
    prob_10, verdict_10, stag_10, incr_10, decr_10, trend_u10, trend_d10 = mill_avgerage(data_train, length, 0.90, print_detailed_info)
    prob_20, verdict_20, stag_20, incr_20, decr_20, trend_u20, trend_d20 = mill_avgerage(data_train, length, 0.80, print_detailed_info)
    prob_33, verdict_33, stag_33, incr_33, decr_33, trend_u33, trend_d33 = mill_avgerage(data_train, length, 0.67, print_detailed_info)
    prob_50, verdict_50, stag_50, incr_50, decr_50, trend_u50, trend_d50 = mill_avgerage(data_train, length, 0.50, print_detailed_info)
    prob_100, verdict_100, stag_100, incr_100, decr_100, trend_u100, trend_d100 = mill_avgerage(data_train, length, 0.00, print_detailed_info)

    outcomes = dict()
    # outcomes["Percent 1"] = [prob_1, verdict_1]
    outcomes["Percent 5"] = [prob_5, verdict_5]
    outcomes["Percent 10"] = [prob_10, verdict_10]
    outcomes["Percent 20"] = [prob_20, verdict_20]
    outcomes["Percent 30"] = [prob_33, verdict_33]
    outcomes["Percent 50"] = [prob_50, verdict_50]
    outcomes["Percent 100"] = [prob_100, verdict_100]

    prob_stagnate = (stag_5 + stag_10 + stag_20 + stag_33 + stag_50 + stag_100) / 6
    prob_increase = (incr_5 + incr_10 + incr_20 + incr_33 + incr_50 + incr_100) / 6
    prob_decrease = (decr_5 + decr_10 + decr_20 + decr_33 + decr_50 + decr_100) / 6
    prob_trend_up = (trend_u5 + trend_u10 + trend_u20 + trend_u33 + trend_u50 + trend_u100) / 6
    prob_trend_dw = (trend_d5 + trend_d10 + trend_d20 + trend_d33 + trend_d50 + trend_d100) / 6
    probabilities = [prob_stagnate, prob_increase, prob_decrease]

    prediction = outcome(probabilities)
    actual = outcome(data_test[0][6:])

    if print_summary_info:
        print("Single highest outcome = {}".format(max(outcomes.items(), key=operator.itemgetter(1))))
        print("Average probability it will stagnate = {:.4}%".format(prob_stagnate * 100))
        print("Average probability it will increase = {:.4}%".format(prob_increase * 100))
        print("Average probability it will decrease = {:.4}%".format(prob_decrease * 100))
        print("Should - {}".format(prediction))
        print("Actual - {}".format(actual))
        print("The total trending up returned = {:.4}%".format(prob_trend_up * 100))
        print("The total trending down returned = {:.4}%\n".format(prob_trend_dw * 100))

    return [prediction, max(probabilities), actual]


# =======================================================
# ==========          Verdict Machine          ==========
# =======================================================


def mill_avgerage(data, data_length, percentage, print_info=False):
    percentage_data = data[round(data_length * percentage):]
    length = len(percentage_data)

    avg_stagnate = 0
    avg_increase = 0
    avg_decrease = 0
    avg_trend_up = 0
    avg_trend_dw = 0

    for item in percentage_data:
        avg_stagnate += item[6]
        avg_increase += item[7]
        avg_decrease += item[8]
        avg_trend_up += item[9]
        avg_trend_dw += item[10]

    outcome_trend_up = avg_trend_up / length
    outcome_trend_dw = avg_trend_dw / length

    outcome_stagnate = avg_stagnate / length
    outcome_increase = avg_increase / length
    outcome_decrease = avg_decrease / length

    core_outcomes = [outcome_stagnate, outcome_increase, outcome_decrease]
    largest_prob = max(core_outcomes)
    verdict = outcome(core_outcomes)

    if print_info:
        print("Looking over the last {} % of data:".format(round((1 - percentage) * 100)))
        print("Items = {}".format(length))
        print("Probability stagnate = {:4.2f} %".format(outcome_stagnate * 100))
        print("Probability increase = {:4.2f} %".format(outcome_increase * 100))
        print("Probability decrease = {:4.2f} %".format(outcome_decrease * 100))
        print("Most likely the next item will - {} -".format(verdict))
        print("Trending up returned = {:4.2f} %".format(outcome_trend_up * 100))
        print("Trending down returned = {:4.2f} %\n".format(outcome_trend_dw * 100))

    return largest_prob, verdict, outcome_stagnate, outcome_increase, outcome_decrease, outcome_trend_up, outcome_trend_dw


# =======================================================
# ==========          Grunt functions          ==========
# =======================================================


def outcome(values):
    descriptions = ["Stagnate", "Increase", "Decrease"]
    return descriptions[values.index(max(values))]


def evaluate(value):
    if value == "Stagnate":
        return 0
    elif value == "Increase":
        return 1
    elif value == "Decrease":
        return -1