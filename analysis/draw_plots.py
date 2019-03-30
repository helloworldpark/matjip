import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from utils.excel import from_excel
from scipy.stats import gaussian_kde, norm, linregress
from sklearn.mixture import GaussianMixture


def plot_dist(columns, labels, colors, do_log, include_missing, title):

    for col, label, color, log in zip(columns, labels, colors, do_log):
        data = google_tabelog[col]
        if not include_missing:
            data = data[data != -1]
        if log:
            data = np.log(1 + data)

        plt.hist(data, density=True, color=color, alpha=0.7, label=label)

        density = gaussian_kde(dataset=data)
        density_x = np.linspace(np.amin(data), np.amax(data), 100)
        density_y = density.evaluate(density_x)
        plt.plot(density_x, density_y, '--', color=color, alpha=1.0)

        if log:
            old_axes = plt.axes()
            old_axes.xaxis.set_major_locator(plt.LogLocator(base=np.e))
            plt.sca(old_axes)
            dx0, dx1 = np.amin(data), np.amax(data)
            ticks = np.linspace(dx0, dx1, 5)
            plt.xticks(ticks=ticks, labels=['{:d}'.format(int(x)) for x in np.exp(ticks)])

    plt.title(title)
    plt.legend()
    plt.savefig('tmp/{:s}.png'.format(title))
    plt.show()


def gaussian_mixture_model(column):
    data = google_tabelog[column]
    data = data[data != -1]

    gmm = GaussianMixture(n_components=2, covariance_type='tied', tol=1e-6, max_iter=100000)
    gmm.fit(X=np.reshape(data.values, (-1, 1)))

    print(gmm.converged_)

    if gmm.converged_:

        print(gmm.covariances_)
        print(gmm.means_)
        print(gmm.precisions_)

        x = np.linspace(np.min(data) - 0.1, np.max(data) + 0.1, 100)
        if gmm.covariance_type == 'full':
            cov1 = np.sqrt(gmm.covariances_[0][0][0])
            cov2 = np.sqrt(gmm.covariances_[1][0][0])
            y1 = norm.pdf(x, loc=gmm.means_[0][0], scale=cov1)
            y2 = norm.pdf(x, loc=gmm.means_[1][0], scale=cov2)
        elif gmm.covariance_type == 'tied':
            cov1 = np.sqrt(gmm.covariances_[0][0])
            cov2 = np.sqrt(gmm.covariances_[0][0])
            y1 = norm.pdf(x, loc=gmm.means_[0][0], scale=cov1)
            y2 = norm.pdf(x, loc=gmm.means_[1][0], scale=cov2)
        else:
            cov1 = np.sqrt(gmm.covariances_[0][0])
            cov2 = np.sqrt(gmm.covariances_[1][0])
            y1 = norm.pdf(x, loc=gmm.means_[0][0], scale=cov1)
            y2 = norm.pdf(x, loc=gmm.means_[1][0], scale=cov2)

        high, low = (0, 1) if gmm.means_[0] > gmm.means_[1] else (1, 0)
        colors = {low: "#fb8072", high: "#80b1d3"}
        labels = {low: "Relatively Low", high: "Relatively High"}
        curves = {low: y1 if gmm.means_[0] < gmm.means_[1] else y2,
                  high: y2 if gmm.means_[0] < gmm.means_[1] else y1}
        covs = {low: cov1 if gmm.means_[0] < gmm.means_[1] else cov2,
                high: cov2 if gmm.means_[0] < gmm.means_[1] else cov1}

        plt.figure(1)
        N, bins, patches = plt.hist(data, density=True)
        for bin_num, patch in zip(bins, patches):
            patch.set_facecolor(colors[gmm.predict(np.array(bin_num).reshape((-1, 1)))[0]])
            patch.set_alpha(0.7)
        plt.plot(x, curves[0], '--', color=colors[0])
        plt.plot(x, curves[1], '--', color=colors[1])
        plt.text(gmm.means_[low] + 0.025, np.max(curves[low]) - 0.4,
                 s="Mean: {:.2f}\nStd: {:.2f}".format(gmm.means_[low][0], covs[low]),
                 color=colors[low]
                 )
        plt.text(gmm.means_[high] + 0.05, np.max(curves[high]),
                 s="Mean: {:.2f}\nStd: {:.2f}".format(gmm.means_[high][0], covs[high]),
                 color=colors[high])
        plt.title("Gaussian Mixture Model on Tabelog's Reviews, Sapporo")

        legend_elements = [Line2D([0], [0], linestyle='--', markersize=5,
                                  color=colors[i], label=labels[i]) for i in [0, 1]]
        plt.legend(handles=legend_elements, loc='upper right')
        # plt.savefig('tmp/{:s}.png'.format("Gaussian Mixture Model on Tabelog's Reviews, Sapporo"))
        plt.show()


def plot_scatter(columns, labels, title, log):
    filter_col0 = google_tabelog[columns[0]] != -1
    filter_col1 = google_tabelog[columns[1]] != -1
    data = google_tabelog[filter_col0 & filter_col1]

    x = np.log(1+data[columns[0]]) if log[0] else data[columns[0]]
    y = np.log(1+data[columns[1]]) if log[1] else data[columns[1]]

    # Scatterplot
    if columns[2]:
        filter_col2 = google_tabelog[columns[2]] != -1
        data = data[filter_col2]
        x = np.log(1 + data[columns[0]]) if log[0] else data[columns[0]]
        y = np.log(1 + data[columns[1]]) if log[1] else data[columns[1]]

        c = np.log(1+data[columns[2]]) if log[2] else data[columns[2]]
        bin_edges = np.histogram_bin_edges(np.unique(c), bins=5)
        c_bin_idx = np.digitize(c, bin_edges, right=False)
        c_binned = np.array([bin_edges[i if i < len(bin_edges) else i-1] for i in c_bin_idx])

        cmap = get_cmap('rainbow')
        normalizer = Normalize(vmin=bin_edges[0], vmax=bin_edges[-1])
        path = plt.scatter(x, y, s=5, alpha=0.5, c=c_binned, cmap=cmap,
                           norm=normalizer, zorder=10)
        axes = path.axes
        x0, x1, y0, y1 = axes.viewLim.x0, axes.viewLim.x1, axes.viewLim.y0, axes.viewLim.y1

        legend_elements = [Line2D([0], [0], marker='.', markersize=5,
                                  linestyle='',
                                  color=cmap(normalizer(bin_edges[i+1])),
                                  label='{0:.1f}~{1:.1f}'.format(np.exp(bin_edges[i]) if log[2] else bin_edges[i],
                                                                 np.exp(bin_edges[i+1]) if log[2] else bin_edges[i+1])
                                  )
                           for i in range(len(bin_edges)-1)]
        plt.legend(handles=legend_elements, title=labels[2], loc=(0.655, 0.11))

    else:
        lines = plt.plot(x, y, color="#404040", marker='.', markersize=5, linestyle='',
                         alpha=0.5, zorder=10)
        axes = lines[0].axes
        x0, x1, y0, y1 = axes.viewLim.x0, axes.viewLim.x1, axes.viewLim.y0, axes.viewLim.y1

    # Linear Regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_value *= r_value
    print("Slope: {:.2f} Intercept: {:.2f} R2: {:.4f} p-value: {:.4f}, Std Err: {:.2f}".format(
        slope, intercept, r_value, p_value, std_err
    ))
    plt.plot(x, intercept + x * slope, color='#2c7bb6', alpha=1.0, linestyle='-', linewidth=2, label='fitted line', zorder=11)
    if log[0] and log[1]:
        lingress_text = r'$\log y={a:.2f} \log x{b}{c:.2f}$'.format(a=slope, b='+' if intercept >= 0.0 else '-',
                                                                    c=np.abs(intercept))
    elif log[0] and not log[1]:
        lingress_text = r'$y={a:.2f}\log x{b}{c:.2f}$'.format(a=slope, b='+' if intercept >= 0.0 else '-',
                                                              c=np.abs(intercept))
    elif not log[0] and log[1]:
        lingress_text = r'$\log y={a:.2f}x{b}{c:.2f}$'.format(a=slope, b='+' if intercept >= 0.0 else '-',
                                                              c=np.abs(intercept))
    else:
        lingress_text = r'$y={a:.2f}x{b}{c:.2f}$'.format(a=slope, b='+' if intercept >= 0.0 else '-',
                                                         c=np.abs(intercept))
    plt.text(x=x0 + (x1 - x0) * 0.65, y=y1, s=lingress_text)
    lingress_text = r'$R^{{2}}={d:.2f}, p={e:.4f}$'.format(d=r_value, e=p_value)
    plt.text(x=x0 + (x1 - x0) * 0.65, y=y1 - (y1 - y0) * 0.048, s=lingress_text)
    lingress_text = r'$\epsilon^{{2}}={f:.3f}$'.format(f=std_err)
    plt.text(x=x0 + (x1 - x0) * 0.65, y=y1 - (y1 - y0) * 0.048 * 2, s=lingress_text)

    # x-hist
    hist_height = (y1 - y0) * 0.2
    density = gaussian_kde(dataset=x)
    density_x = np.linspace(x0, x1)
    density_y = density.evaluate(density_x)
    density_y = (density_y / np.amax(density_y)) * hist_height + y0
    plt.plot(density_x, density_y, '--', color='#1a9641', alpha=0.7, zorder=9)
    plt.fill_between(x=density_x, y1=density_y, y2=y0, color='#1a9641', alpha=0.3, zorder=9)

    # y-hist
    hist_height = (x1 - x0) * 0.2
    density = gaussian_kde(dataset=y)
    density_x = np.linspace(y0, y1)
    density_y = density.evaluate(density_x)
    density_y = (density_y / np.amax(density_y)) * hist_height + x0
    plt.plot(density_y, density_x, '--', color='#d7191c', alpha=0.7, zorder=9)
    plt.fill_betweenx(y=density_x, x1=density_y, x2=x0, color='#d7191c', alpha=0.3, zorder=9)

    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
    plt.title(title)
    if log[0]:
        old_axes = plt.axes()
        old_axes.xaxis.set_major_locator(plt.LogLocator(base=np.e))
        plt.sca(old_axes)
        dx0, dx1 = axes.dataLim.x0, axes.dataLim.x1
        ticks = np.linspace(dx0, dx1, 5)
        plt.xticks(ticks=ticks, labels=['{:d}'.format(int(x)) for x in np.exp(ticks)])

    if log[1]:
        old_axes = plt.axes()
        old_axes.yaxis.set_major_locator(plt.LogLocator(base=np.e))
        plt.sca(old_axes)
        dy0, dy1 = axes.dataLim.y0, axes.dataLim.y1
        ticks = np.linspace(dy0, dy1, 5)
        plt.yticks(ticks=ticks, labels=['{:d}'.format(int(x)) for x in np.exp(ticks)])
    plt.savefig('tmp/{:s}.png'.format(title))
    plt.show()


if __name__ == '__main__':
    google_tabelog = from_excel(file_path="../googleplaces/tmp/google_tabelog_sapporo.xlsx")
    print("Loaded {:d}x{:d} records".format(google_tabelog.shape[0], google_tabelog.shape[1]))
    print("Columns: {}".format(google_tabelog.columns.values))
    # plot_dist(columns=['rating'],
    #           labels=['Tabelog'],
    #           colors=['#2c7bb6'],
    #           include_missing=False,
    #           title='Histogram of Tabelog Ratings in Sapporo')
    # plot_dist(columns=['google_rating'],
    #           labels=['Google'],
    #           colors=['#fdae61'],
    #           include_missing=False,
    #           title='Histogram of Google Ratings in Sapporo')
    # plot_dist(columns=['rating', 'google_rating'],
    #           labels=['Tabelog', 'Google'],
    #           colors=['#2c7bb6', '#fdae61'],
    #           include_missing=False,
    #           title='Histogram of Tabelog and Google Ratings in Sapporo')

    # plot_dist(columns=['price_noon'],
    #           labels=['Tabelog'],
    #           colors=['#2c7bb6'],
    #           include_missing=False,
    #           do_log=[True],
    #           title='Log-Histogram of Tabelog Price at Noon in Sapporo')

    # plot_dist(columns=['google_review_en'],
    #           labels=['Google'],
    #           colors=['#fdae61'],
    #           include_missing=False,
    #           do_log=[False],
    #           title='Histogram of Google English-Review Count in Sapporo')

    # gaussian_mixture_model(column='rating')
    # plot_scatter(columns=['google_user_ratings_total', 'reviews', 'google_review_en'],
    #              labels=['Tabelog', 'Google', '# of Reviews'],
    #              title='Scatterplot of Ratings (w/o Missing Data)',
    #              log=[True, True, False])

    # plot_scatter(columns=['reviews', 'rating', ''],
    #              labels=['Reviews', 'Rating', ''],
    #              title="Scatterplot of Tabelog's Rating vs Reviews",
    #              log=[False, False, False])

    # plot_scatter(columns=['rating', 'reviews', ''], labels=['Rating', 'Num. of Reviews', ''],
    #              title='Scatterplot of Rating vs Num. of Reviews (w/o missing data)', log=[False, True, True])

    # plot_scatter(columns=['google_user_ratings_total', 'google_rating', 'google_review_en'],
    #              labels=['Reviews', 'Rating', 'Reviews in English'],
    #              title="Scatterplot of Google's Rating vs Reviews",
    #              log=[True, False, False])

    # plot_scatter(columns=['google_review_en', 'google_user_ratings_total', ''],
    #              labels=['English Reviews', 'Rating Counts', ''],
    #              title="Scatterplot of Google's English Reviews vs Rating Count",
    #              log=[False, True, False])

    plot_scatter(columns=['rating', 'google_rating', 'google_review_en'],
                 labels=['Reviews', 'Rating', 'English Reviews'],
                 title="Scatterplot of Rating",
                 log=[False, False, True])


