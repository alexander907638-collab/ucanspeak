<script setup lang="ts">
import { useToast } from 'primevue/usetoast';

const { $api } = useNuxtApp()
const toast = useToast()

const pupils = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const isEditing = ref(false)
const selectedPupil = ref(null)

const defaultForm = () => ({
  full_name: '',
  email: '',
  max_logins: 1,
  password: '',
})

const form = ref(defaultForm())

async function fetchPupils() {
  loading.value = true
  try {
    pupils.value = await $api.school.list()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить учеников', life: 3000 })
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  form.value = defaultForm()
  dialogVisible.value = true
}

function openEditDialog(pupil) {
  isEditing.value = true
  selectedPupil.value = pupil
  form.value = { ...pupil }
  dialogVisible.value = true
}

function openDeleteDialog(pupil) {
  selectedPupil.value = pupil
  deleteDialogVisible.value = true
}

async function submitForm() {
  try {
    const payload = { ...form.value }
    if (isEditing.value && !payload.password) {
      delete payload.password
    }
    if (isEditing.value) {
      await $api.school.update(selectedPupil.value.id, form.value)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Ученик обновлён', life: 3000 })
    } else {
      await $api.school.create(form.value)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Ученик добавлен', life: 3000 })
    }
    dialogVisible.value = false
    await fetchPupils()
  } catch (e) {
    const detail = e?.data?.detail || 'Произошла ошибка'
    toast.add({ severity: 'error', summary: 'Ошибка', detail, life: 4000 })
  }
}


async function deletePupil() {
  try {
    await $api.school.destroy(selectedPupil.value.id)
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Ученик удалён', life: 3000 })
    deleteDialogVisible.value = false
    await fetchPupils()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось удалить ученика', life: 3000 })
  }
}

  async function logout(data) {
    loading.value = true
    try {
      await $api.school.force_logout_pupil(data.id)
      toast.add({
        severity: 'success',
        summary: 'Готово',
        detail: `Ученик ${data.full_name || data.email} разлогинен на всех устройствах`,
        life: 3000
      })
    } catch (e: any) {
      const detail = e?.data?.detail || 'Не удалось разлогинить ученика'
      toast.add({
        severity: 'error',
        summary: 'Ошибка',
        detail,
        life: 4000
      })
    } finally {
      loading.value = false
    }
  }

await fetchPupils()
useSeoMeta({
  title: `Ученики `,
})
</script>

<template>
  <CardBase padding="md">
    <div class="flex items-center justify-between mb-6">
      <TypingText28 text="Ученики" />
      <Button label="Добавить ученика" icon="pi pi-plus" @click="openCreateDialog" />
    </div>

    <DataTable
        :value="pupils"
        :loading="loading"
        stripedRows
        emptyMessage="Ученики не найдены"
    >
      <Column field="full_name" header="ФИО" />
      <Column field="email" header="Email" />
      <Column field="max_logins" header="Макс. подключений" />
      <Column header="Действия" style="width: 120px">
        <template #body="{ data }">
          <div class="flex gap-2">
            <Button icon="pi pi-sign-out" severity="warn" size="small" text @click="logout(data)" />
            <Button icon="pi pi-pencil" severity="secondary" size="small" text @click="openEditDialog(data)" />
            <Button icon="pi pi-trash" severity="danger" size="small" text @click="openDeleteDialog(data)" />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Диалог создания/редактирования -->
    <Dialog
        v-model:visible="dialogVisible"
        :header="isEditing ? 'Редактировать ученика' : 'Добавить ученика'"
        modal
        style="width: 420px"
    >
      <div class="flex flex-col gap-4 pt-2">
        <UIInput
            fluid
            placeholder="ФИО"
            label="ФИО"
            id="username"
            v-model="form.full_name"
        />
        <UIInput
            fluid
            placeholder="Email"
            label="Email"
            id="email"
            v-model="form.email"
        />
        <UIInput
            fluid
            placeholder="Пароль"
            label="Пароль"
            id="password"
            type="password"
            v-model="form.password"
            :required="!isEditing"
        />
        <small v-if="isEditing" class="text-gray-400">Оставьте пустым, чтобы не менять пароль</small>

        <!-- Кол-во подключений через InputNumber -->
        <div class="flex flex-col gap-1">
          <label for="max_logins" class="text-sm font-medium">Макс. подключений</label>
          <InputNumber
              id="max_logins"
              v-model="form.max_logins"
              :min="1"
              showButtons
              buttonLayout="horizontal"
              fluid
              :allowEmpty="false"
          >
            <template #decrementbuttonicon>
              <span class="pi pi-minus" />
            </template>
            <template #incrementbuttonicon>
              <span class="pi pi-plus" />
            </template>
          </InputNumber>
        </div>
      </div>

      <template #footer>
        <Button label="Отмена" severity="secondary" text @click="dialogVisible = false" />
        <Button :label="isEditing ? 'Сохранить' : 'Добавить'" @click="submitForm" />
      </template>
    </Dialog>

    <!-- Диалог подтверждения удаления -->
    <Dialog
        v-model:visible="deleteDialogVisible"
        header="Удалить ученика"
        modal
        style="width: 360px"
    >
      <p>Вы уверены, что хотите удалить ученика <b>{{ selectedPupil?.full_name }}</b>?</p>
      <template #footer>
        <Button label="Отмена" severity="secondary" text @click="deleteDialogVisible = false" />
        <Button label="Удалить" severity="danger" @click="deletePupil" />
      </template>
    </Dialog>


  </CardBase>
</template>