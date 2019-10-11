import json
import numpy as np
import pandas as pd
import wordcloud as cloud
import matplotlib.pyplot as plt

# -----------------------------Constants-------------------------------------

# fs stands for FontSize. It set font size text on x axis for all graphs
fs = 6

# Set the bar width for all graphs
bars_width = 0.3

# Set text angle on x axis for all graphs
x_text_angle = 45

# Set the maximum words to be rendered for all word clouds
wc_max_words = 10

# Set the maximum word length for all word clouds
wc_max_words_length = 25

# Determines if output will be render on screen
show_on_screen = True

# Determines if output will be render as PDF files
save_figures_as_PDF_files = True

# List of summable columns
head = ['views', 'likes', 'dislikes', 'comment_count']

# List of columns to render as word clouds
wc_search = ['title', 'tags', 'description']

# List of time to render as line graph
time_search = ['month', 'day', 'hour']

# List of files to be processed
files = {
    'US': ['input/USVideos.csv', 'input/US_category_id.json', 'ISO-8859-1'],
    #'RU': ['input/RUVideos.csv', 'input/RU_category_id.json', 'ISO-8859-1'],
    #'MX': ['input/MXVideos.csv', 'input/MX_category_id.json', 'ISO-8859-1'],
    #'KR': ['input/KRVideos.csv', 'input/KR_category_id.json', 'UTF8'],
    #'JP': ['input/JPVideos.csv', 'input/JP_category_id.json', 'ISO-8859-1'],
    #'IN': ['input/INVideos.csv', 'input/IN_category_id.json', 'ISO-8859-1'],
    #'GB': ['input/GBVideos.csv', 'input/GB_category_id.json', 'ISO-8859-1'],
    #'FR': ['input/FRVideos.csv', 'input/FR_category_id.json', 'ISO-8859-1'],
    #'DE': ['input/DEVideos.csv', 'input/DE_category_id.json', 'ISO-8859-1'],
    #'CA': ['input/CAVideos.csv', 'input/CA_category_id.json', 'ISO-8859-1'],
}

# -----------------------------Variables-------------------------------------

# List of created figures
figures = []


# -----------------------------Functions-------------------------------------

def main():
    for file in files.items():

        # -------------------Loading Data From Files-----------------------

        country = file[0]
        frame = pd.read_csv(file[1][0], encoding=file[1][2])
        categories = get_categories(file[1][1])

        # ---------------------Print Basic Data----------------------------

        print(f'{country} Data:')
        print(frame.info(), frame.shape, frame.describe())
        print('-----------------------------------------')
        print('\n'*2)

        # --------------------Plotting Basic Inputs------------------------

        plot_as_bar(
            ax=create_figure(f'{country} - Basic input'),
            y_label='Interactions',
            x_texts=head,
            data={'data': list(frame[h][1] for h in head)} #Count per head
        )

        # -----------------Plotting Category Data------------------------

        category_data = frame['category_id'].value_counts().rename(categories)

        plot_as_bar(
            ax=create_figure(f'{country} - Categories'),
            y_label='Totals',
            x_texts=category_data.keys(),
            data={'data': category_data}
        )

        # ----------Plotting Percentage of Interactions------------------

        plot_as_bar(
            ax=create_figure(f'{country} - Interactions per Category'),
            y_label='Percentage',
            x_texts=category_data.keys(),
            data=get_interaction_percentage(frame)
        )

        # -------------------Rendering Word Clouds-----------------------

        for wc in wc_search:
            plot_word_cloud(
                ax=create_figure(f'{country} - Word Cloud {wc}'),
                data=frame,
                desc=wc
            )

        # --------------------Plotting Time Analysis----------------------

        dt = pd.to_datetime(frame['publish_time']).dt
        frame['month'] = dt.month
        frame['day'] = dt.day
        frame['hour'] = dt.hour

        for time in time_search:
            plot_as_lines(
                ax=create_figure(f'{country} - Interactions Per {time}'),
                y_label='Interactions',
                timely_data=frame.groupby(time)
            )

    # ------------------Creating Output-----------------------------------

    if show_on_screen:
        plt.show()

    if save_figures_as_PDF_files:
        for figure in figures:
            figure.savefig(f'output/{figure._suptitle.get_text()}.pdf')

    # ------------------Cleaning up and Bye-------------------------------

    plt.close()
    exit(0)


def to_dictionary(data):
    """
    Creates a dictionary from an aggregated DataFrame by sum
    Example:
        Likes:100
        Dislikes:20
        comment_count:5
    """

    return dict((h, data[h, 'sum']) for h in head[1:4])


def create_figure(title):
    """
    Create a new figure and sets its title
    """

    fig = plt.figure()
    figures.append(fig)
    fig.canvas.set_window_title(title)
    fig.suptitle(title)
    return fig.add_subplot(111)


def sum_up(group):
    """
    Creates an aggregate by sum using the required column headers
    """

    return group.aggregate(dict((h, ['sum']) for h in head))


def get_categories(f):
    """
    returns a dic with id,category entries
    1: technology,
    2: Social and News
    ...
    """

    with open(f) as raw_json:
        items = pd.DataFrame(json.load(raw_json))['items']
        return dict((int(i['id']), i['snippet']['title']) for i in items)


def get_interaction_percentage(data):
    """
    Creates an aggregate from a DataFrame by getting the percentage of
    likes, dislikes and comments according to views
    """

    group = sum_up(data.groupby('category_id'))
    views = group[head[0], 'sum'] * 100
    return dict((h, group[h, 'sum'] / views) for h in head[1:4])


def text_format(ax, y_label, x_texts):
    """
    Add labels and texts to an axis Figure
    """

    ax.set_ylabel(y_label)
    ax.set_xticks(np.arange(len(x_texts)) + bars_width)
    plt.setp(ax.set_xticklabels(x_texts), rotation=x_text_angle, fontsize=fs)


def plot_as_bar(ax, y_label, x_texts, data):
    """
    creates a bar graph using a dataframe input for a figure
    """
    space = np.arange(len(x_texts))
    bars = []

    for totals in data.values():
        bars.append(ax.bar(space, totals, bars_width))
        space = space + bars_width

    ax.legend(bars, data.keys())
    text_format(ax, y_label, x_texts)


def plot_as_lines(ax, y_label, timely_data):
    """
    Creates a line graph using a DataFrame input for a figure
    """

    space = np.arange(len(timely_data.indices))

    for totals in to_dictionary(sum_up(timely_data)).values():
        ax.plot(space, totals, bars_width)
        space = space + bars_width

    text_format(ax, y_label, timely_data.indices)


def plot_word_cloud(ax, data, desc):
    """
    Creates a word cloud by column(desc)
    """

    w = cloud.WordCloud(max_words=wc_max_words)
    value_counts = data[desc].str[:wc_max_words_length].value_counts()
    img = w.generate_from_frequencies(value_counts)
    ax.imshow(img)


main()
