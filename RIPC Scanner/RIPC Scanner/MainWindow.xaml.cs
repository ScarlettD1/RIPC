using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows;
using Newtonsoft.Json;
using System.Net.Http;
using System.Text;
using System.Net;
using Saraff.Twain;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Imaging;

namespace RIPC_Scanner
{
    /// <summary>
    /// Логика взаимодействия для MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private string[] parametrs = ((App)Application.Current).Parameters;
        private static readonly HttpClient client = new HttpClient();
        private Twain32 twain = new Twain32();

        public MainWindow()
        {
            InitializeComponent();

            // Установка переданных параметров
            SetParametrs();

            // Обновление списка доступных сканеров
            GetDevices();

        }

        private void updateSButton_Click(object sender, RoutedEventArgs e)
        {
            // Обновление списка доступных сканеров
            GetDevices();
        }


        private void startScanButton_Click(object sender, RoutedEventArgs e)
        {
            // Создание сессии twain
            twain.OpenDSM();

            // Использование выбранного сканера
            twain.SourceIndex = sComboBox.SelectedIndex;

            // Подключение к сканеру
            try
            {
                twain.OpenDataSource();
            }
            catch
            {
                MessageBox.Show("Сканер занят или недоступен.\n" +
                    "При многократной ошибке, попробуйте перезапустить компьютер и сканер.", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);

                // Закрытие сессии twain
                twain.CloseDataSource();
                twain.CloseDSM();
                return;
            }

            // Установка необходимых параметров для сканирования
            try
            {
                twain.SetCap(TwCap.IPixelType, TwPixelType.RGB);
                twain.SetCap(TwCap.XResolution, 300);
                twain.SetCap(TwCap.YResolution, 300);
            }
            catch
            {
                MessageBox.Show($"Не возможно установить минимальные параметры для сканера.\n" +
                    $"Требования: RGB, DPI 300", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);

                // Закрытие сессии twain
                twain.CloseDataSource();
                twain.CloseDSM();
                return;
            }

            // Включение автоматического сканирования
            try
            {
                // twain.SetCap(TwCap.FeederEnabled, sAutoFeederCheckBox.IsChecked);
                twain.SetCap(TwCap.AutoFeed, sAutoFeederCheckBox.IsChecked);
            }
            catch
            {
                if (sAutoFeederCheckBox.IsChecked == true)
                {
                    MessageBox.Show("Не возможно использовать автоматическое сканирование страниц.", "Ошибка!",
                        MessageBoxButton.OK, MessageBoxImage.Error);

                    // Закрытие сессии twain
                    twain.CloseDataSource();
                    twain.CloseDSM();
                    return;
                }
            }

            // Включение двухсторонего сканирования
            try
            {
                twain.SetCap(TwCap.DuplexEnabled, sDuplexCheckBox.IsChecked);
            }
            catch
            {
                if (sDuplexCheckBox.IsChecked == true)
                {
                    MessageBox.Show("Не возможно использовать двухсторонее сканирование страниц.", "Ошибка!",
                                        MessageBoxButton.OK, MessageBoxImage.Error);

                    // Закрытие сессии twain
                    twain.CloseDataSource();
                    twain.CloseDSM();
                    return;
                }
            }

            // Отключение системного интерфейса
            twain.ShowUI = false;

            // Подписываемся на событие завершения сканирования страницы
            twain.EndXfer += twain_EndXfer;

            // Подписываемся на событие ошибки сканирования страницы
            twain.AcquireError += twain_AcquireError;

            // Запуск сканирования
            twain.Acquire();

            // Закрытие сессии twain
            twain.CloseDataSource();
            twain.CloseDSM();
            return;
        }

        private void twain_EndXfer(object sender, EventArgs e)
        {
            // Получаем крайнее отсканированное изображение 
            var scannedImage = twain.GetImage(twain.ImageCount - 1);

            // Переводим изображение в байты
            var byteImage = (byte[])(new ImageConverter()).ConvertTo(scannedImage, typeof(byte[]));

            // Отправляем изображение на сервис
            SendFile(byteImage);

            // Сохраняем крайнюю страницу в файл
            //string fileName = $"C:\\Ripc\\page_{twain.ImageCount}_{DateTime.Now.ToString("MMddHHmmss")}.png";
            //twain.GetImage(twain.ImageCount - 1).Save(fileName, ImageFormat.Jpeg);
        }

        private void twain_AcquireError(object sender, EventArgs e)
        {
            MessageBox.Show("Не возможно использовать автоматическое сканирование страниц.", "Ошибка!",
                             MessageBoxButton.OK, MessageBoxImage.Error);

            // Закрытие сессии twain
            twain.CloseDataSource();
            twain.CloseDSM();
            return;
        }

        private void GetDevices()
        {
            // Очистка текущего списка сканеров
            sComboBox.Items.Clear();

            // Создание сессии twain
            try { twain.OpenDSM(); } catch { }

            // Закрытие сессии twain
            twain.CloseDSM();

            // Проход по найденым сканерам
            for (int i = 0; i < twain.SourcesCount; i++)
            {
                // Заполнение списка сканерами
                sComboBox.Items.Add(twain.GetSourceProductName(i));
            }

            // Проверка наличия сканеров
            if (sComboBox.Items.Count == 0)
            {
                MessageBox.Show("Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);

                // Отключение кнопки сканирования
                startScanButton.IsEnabled = false;

                return;
            }

            // Включение кнопки сканирования
            startScanButton.IsEnabled = true;

            // Установка изначального сканера
            sComboBox.SelectedIndex = 0;

            return;
        }

        private void SetParametrs()
        {
            // Установка ID мероприятия
            eventIDNum.Content = parametrs[0];
        }

        private async void SendFile(byte[] file)
        {
            var data = new
            {
                event_id = eventIDNum.Content,
                byte_file = file
            };

            // Сериализуем данные в JSON строку
            var json = JsonConvert.SerializeObject(data);

            // Создаем HTTP клиент и отправляем POST запрос
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await client.PostAsync("", content);

            // Проверяем ответ
            if (!response.IsSuccessStatusCode)
            {
                throw new Exception(response.StatusCode.ToString());
            }
            return;
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            // Закрытие сессии twain
            twain.CloseDataSource();
            twain.CloseDSM();

            base.OnClosing(e);
            return;
        }

    }
}
